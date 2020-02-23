from django.views.generic import ListView

from django.db.models import F
from django.db.models.expressions import RawSQL

from . import models as m


class NewsList(ListView):
    model = m.CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_news.html'
    paginate_by = 25


class RelevantNews(ListView):
    model = m.CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_relevant.html'
    paginate_by = 25

    def get_queryset(self):
        queryset = (m.CnnNews.objects.extra(tables=[m.GoogleTrendsAtom._meta.db_table])
                    .annotate(key_title=RawSQL('{}.{}'.format(m.GoogleTrendsAtom._meta.db_table, m.GoogleTrendsAtom.title.field.name), ()))
                    .filter(title__icontains=F('key_title'))
                    .order_by('-posted')
                    .distinct())
        return queryset


class GoogleTrends(ListView):
    """
    List all google trends
    """

    model = m.GoogleTrendsAtom
    context_object_name = 'trends_collection'
    template_name = 'google_trends.html'
    paginate_by = 50
