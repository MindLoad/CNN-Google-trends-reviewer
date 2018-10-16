from django.views.generic import ListView

from django.db.models import F
from django.db.models.expressions import RawSQL

from .models import GoogleTrendsAtom, CnnNews


class NewsList(ListView):
    model = CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_news.html'
    paginate_by = 25


class RelevantNews(ListView):
    model = CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_relevant.html'
    paginate_by = 25

    def get_queryset(self):
        queryset = (CnnNews.objects.extra(tables=[GoogleTrendsAtom._meta.db_table])
                    .annotate(key_title=RawSQL('{}.{}'.format(GoogleTrendsAtom._meta.db_table, GoogleTrendsAtom.title.field_name), ()))
                    .filter(title__icontains=F('key_title'))
                    .distinct())
        return queryset
