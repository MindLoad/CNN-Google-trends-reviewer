"""
Celery tasks for interact with RSS
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task

import pytz
import feedparser
from time import mktime
import datetime
from bs4 import BeautifulSoup
import pysolr

from django.utils import timezone
from django.conf import settings

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
    added_channels = 0
    for each in feed_channels:
        if each.text and each.text.endswith('.rss') and each.text not in (channel['url'] for channel in existed_channels):
            CnnChannels.objects.add_channel(each.text)
            added_channels += 1
    return f"Add channels: {added_channels}"


@shared_task
def task_cnn_news_parser() -> str:
    """
    :Schedule: every half hour
    :description: collect CNN news from each channel
    """

    solr = pysolr.Solr(settings.SOLR_HOST, timeout=10, always_commit=True)
    cnn_channel = CnnChannels.objects.all()
    if not cnn_channel:
        return f"No CNN channels..."
    existed_news = CnnNews.objects.values('title')
    for channel in cnn_channel:
        parser = feedparser.parse(channel.url)
        added_news = 0
        for feed in parser.entries:
            if not feed.title or feed.title in (news['title'] for news in existed_news):
                continue
            try:
                posted = datetime.datetime.fromtimestamp(mktime(feed.published_parsed)).replace(tzinfo=pytz.UTC)
            except (KeyError, AttributeError, TypeError) as error:
                print(f"RSS Parse Error: {error}")
                posted = timezone.now()
            finally:
                added_news += 1
            news = CnnNews.objects.add_news(channel, feed.title, feed.link, posted)
            solr.add([
                {
                    "title": feed.title,
                    "news_id": news.id,
                    "posted": posted.isoformat()
                }
            ])
        return f"Add news: {added_news}"


@shared_task
def task_delete_old_records() -> None:
    """
    :Schedule: everyday, at 23:59
    :description: delete objects from CnnNew & GoogleTrendsAtom models older than week
    """

    previous_week = timezone.now() - timezone.timedelta(days=7)
    old_trends = GoogleTrendsAtom.objects.filter(created__lt=previous_week)
    old_trends.delete()
    old_news = CnnNews.objects.filter(created__lt=previous_week)
    old_news.delete()
