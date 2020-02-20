"""
Parsers class
"""

__all__ = [
    'TrendsParser',
    'ChannelParser',
    'NewsParser'
]

import pytz
import typing
import datetime
import feedparser

from time import mktime

from bs4 import BeautifulSoup
from returns import maybe

from .models import GoogleTrendsAtom


class TrendsParser:
    """
    Parse google HotTrends
    """

    GOOGLE_TRENDS_HOURLY_ATOM = 'https://trends.google.com/trends/hottrends/atom/hourly'

    @classmethod
    @maybe.maybe
    def parse(cls) -> typing.Optional[list]:
        """
        parse google trends atom rss
        """

        parser = feedparser.parse(cls.GOOGLE_TRENDS_HOURLY_ATOM)
        if parser.status != 200 or not getattr(parser, 'entries', False):
            return None
        existed = GoogleTrendsAtom.objects.values_list('snippet', flat=True)
        result = [
            GoogleTrendsAtom(
                title=entry.title,
                url=entry.ht_news_item_url,
                published=datetime.datetime.fromtimestamp(mktime(entry.published_parsed)).replace(tzinfo=pytz.UTC),
                snippet=cls.bs4_encode(entry.ht_news_item_snippet)
            ) for entry in parser.entries if cls.bs4_encode(entry.ht_news_item_snippet) not in existed
        ]
        return result

    @staticmethod
    def bs4_encode(
            text: str
    ) -> str:
        """
        encode html string with special characters
        """
        return BeautifulSoup(
            text,
            features="html.parser"
        ).decode_contents()


class ChannelParser:
    """
    Parse google channels
    """


class NewsParser:
    """
    Parse google news
    """
