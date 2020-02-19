"""
Celery tasks for interact with RSS
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task

import pytz
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import mktime

from returns import pipeline as pipeline_monad

from .models import GoogleTrendsAtom, CnnChannels, CnnNews
from . import parser as atom_parser

CNN_RSS_LIST_URL = 'http://edition.cnn.com/services/rss/'


@shared_task
def task_google_trends_parser() -> None:
    """
    Shedule: every hour
    :description: add Google trends
    """

    trends = atom_parser.TrendsParser.parse()
    if not pipeline_monad.is_successful(trends):
        return

    saved_trends = GoogleTrendsAtom.objects.values('title', 'updated')

    if trends_updated in (trend['updated'] for trend in all_trends):
        return
    trends_content = parser.entries[0].content[0].value
    trends_links = BeautifulSoup(trends_content, 'lxml').find_all('a')
    for each in trends_links:
        if each.text not in (trend['title'] for trend in all_trends):
            GoogleTrendsAtom.objects.add_trend(each.text, each['href'], trends_updated)


@shared_task
def task_cnn_channels_parser() -> None:
    """
    :Shedule: everyday, at 23:49
    :description: update CnnChannels Model from main Cnn page
    """

    make_request = requests.get(CNN_RSS_LIST_URL)
    if make_request.status_code != 200:
        return
    parser = BeautifulSoup(make_request.text, 'html.parser')
    feed_channels = parser.find_all('a')
    existed_channels = CnnChannels.objects.values('url')
    for each in feed_channels:
        if each.text and each.text.endswith('.rss') and each.text not in (channel['url'] for channel in existed_channels):
            CnnChannels.objects.add_channel(each.text)


@shared_task
def task_cnn_news_parser() -> None:
    """
    :Schedule: every half hour
    :description: collect CNN news from each channel
    """

    cnn_channel = CnnChannels.objects.all()
    if cnn_channel.count() == 0:
        return
    existed_news = CnnNews.objects.values('title')
    for channel in cnn_channel:
        parser = feedparser.parse(channel.url)
        for feed in parser.entries:
            if not feed.title or feed.title in (news['title'] for news in existed_news):
                continue
            try:
                posted = datetime.fromtimestamp(mktime(feed.published_parsed)).replace(tzinfo=pytz.UTC)
            except (KeyError, AttributeError, TypeError) as error:
                print(f"RSS Parse Error: {error}")
                posted = datetime.now().replace(tzinfo=pytz.UTC)
            CnnNews.objects.add_news(channel, feed.title, feed.link, posted)


@shared_task
def task_delete_old_records() -> None:
    """
    :Schedule: everyday, at 23:59
    :description: delete objects from CnnNew & GoogleTrendsAtom models older than week
    """

    previous_week = datetime.now() - timedelta(days=7)
    old_trends = GoogleTrendsAtom.objects.filter(created__lt=previous_week)
    old_trends.delete()
    old_news = CnnNews.objects.filter(created__lt=previous_week)
    old_news.delete()
