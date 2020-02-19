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

from returns import maybe


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
        result = [
            {
                "title": entry.title,
                "published_parsed": datetime.datetime.fromtimestamp(
                    mktime(entry.published_parsed)
                ).replace(tzinfo=pytz.UTC),
                "snippet": entry.ht_news_item_snippet,
            } for entry in parser.entries
        ]
        return result


class ChannelParser:
    """
    Parse google channels
    """


class NewsParser:
    """
    Parse google news
    """
