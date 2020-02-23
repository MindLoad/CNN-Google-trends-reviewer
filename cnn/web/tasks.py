"""
Celery tasks for interact with RSS
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task

import pytz
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import mktime

from returns import pipeline as pipeline_monad

from .models import GoogleTrendsAtom, CnnChannels, CnnNews
from . import parser as parsers


@shared_task
def task_google_trends_parser() -> str:
    """
    Shedule: every hour
    :description: add Google trends
    """

    trends = parsers.TrendsParser.parse()
    if not pipeline_monad.is_successful(trends):
        return f"Error parsing google trends"

    trends = trends.unwrap()
    GoogleTrendsAtom.objects.bulk_create(trends)

    return f"Added trends: {len(trends)}"


@shared_task
def task_cnn_channels_parser() -> str:
    """
    :Shedule: everyday, at 23:49
    :description: update CnnChannels Model from main Cnn page
    """

    response = parsers.ChannelParser.parse()
    if not pipeline_monad.is_successful(response):
        return "Error while trying to get Cnn news channels"
    parser = BeautifulSoup(response.unwrap().text, 'html.parser')
    feed_channels = parser.find_all('a')
    existed_channels = CnnChannels.objects.values('url')
    for each in feed_channels:
        if each.text and each.text.endswith('.rss') and each.text not in (channel['url'] for channel in existed_channels):
            CnnChannels.objects.add_channel(each.text)
    return f"Add channels: {len(feed_channels)}"


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
