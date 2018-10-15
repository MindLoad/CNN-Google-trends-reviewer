from __future__ import absolute_import, unicode_literals
from celery import shared_task

import pytz
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import mktime

from .models import GoogleTrendsAtom, CnnChannels, CnnNews

GOOGLE_TRENDS_HOURLY_ATOM = 'https://trends.google.com/trends/hottrends/atom/hourly'
CNN_RSS_LIST_URL = 'http://edition.cnn.com/services/rss/'


@shared_task
def task_google_trends_parser():
    """
    Shedule: every hour
    :description: add Google trends
    :return: GoogleTrendsAtom
    """
    parser = feedparser.parse(GOOGLE_TRENDS_HOURLY_ATOM)
    if parser.status != 200 or len(parser.entries) != 1:
        return
    trends_updated = parser.feed.updated_parsed
    convert_to_datetime = datetime.fromtimestamp(mktime(trends_updated)).replace(tzinfo=pytz.UTC)
    trends_exists = GoogleTrendsAtom.objects.filter(updated=convert_to_datetime)
    if trends_exists.count() > 0:
        return
    trends_content = parser.entries[0].content[0].value
    trends_links = BeautifulSoup(trends_content, 'lxml').find_all('a')
    for each in trends_links:
        GoogleTrendsAtom.objects.add_trend(each.text, each['href'], convert_to_datetime)
        print(f"ADD RECORD TO DB: {each.text}")


@shared_task
def task_cnn_channels_parser():
    """
    :Shedule: everyday, at 23:59
    :description: update CnnChannels Model from main Cnn page
    :return: CnnChannel
    """

    make_request = requests.get(CNN_RSS_LIST_URL)
    parser = BeautifulSoup(make_request.text, 'html.parser')
    cnn_links = parser.find_all('a')
    existed_channel = CnnChannels.objects.all()
    for each in cnn_links:
        print(f'CNN-RSS url: {each.text}')
        if each.text and each.text.endswith('.rss') and each.text not in [channel.url for channel in existed_channel]:
            print('add rss to CnnRssList')
            CnnChannels.objects.add_channel(each.text)


@shared_task
def task_cnn_news_parser():
    """
    :Schedule: every half hour
    :description: collect CNN news from each channel
    :return: CnnNews
    """
    cnn_channel = CnnChannels.objects.all()
    if cnn_channel.count() == 0:
        return
    existed_news = CnnNews.objects.all()
    for channel in cnn_channel:
        print(f"Start parse the channel: {channel.url}")
        parser = feedparser.parse(channel.url)
        for feed in parser.entries:
            if not feed.title or feed.title in [news.title for news in existed_news]:
                continue
            try:
                posted = datetime.fromtimestamp(mktime(feed.published_parsed)).replace(tzinfo=pytz.UTC)
            except (KeyError, AttributeError) as error:
                print(f"RSS Parse Error: {error}")
                posted = datetime.now().replace(tzinfo=pytz.UTC)
            CnnNews.objects.add_news(channel, feed.title, feed.link, posted)


@shared_task
def task_delete_old_records():
    """
    :Schedule: everyday
    :description: delete objects from CnnNew & GoogleTrendsAtom models older than week
    :return:
    """

    previous_week = datetime.now() - timedelta(days=7)
    old_trends = GoogleTrendsAtom.objects.filter(created__lt=previous_week)
    old_trends.delete()
    old_news = CnnNews.objects.filter(created__lt=previous_week)
    old_news.delete()
