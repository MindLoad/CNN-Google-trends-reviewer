"""
Parsers class
"""

__all__ = [
    'TrendsParser',
    'ChannelParser',
    'NewsParser'
]

import feedparser

from returns import result as result_monada


class TrendsParser:
    """
    Parse google HotTrends
    """

    GOOGLE_TRENDS_HOURLY_ATOM = 'https://trends.google.com/trends/hottrends/atom/hourly'

    @classmethod
    def parse(cls):
        """
        parse google trends atom rss
        """

        parser = feedparser.parse(cls.GOOGLE_TRENDS_HOURLY_ATOM)
        if parser.status != 200:
            return result_monada.Failure(parser.status)



class ChannelParser:
    """
    Parse google channels
    """


class NewsParser:
    """
    Parse google news
    """
