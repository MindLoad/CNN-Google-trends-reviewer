from django.views.generic import ListView
from django.db.models import Subquery
from django.db.models import CharField, Value

from .models import GoogleTrendsAtom, CnnNews


class NewsList(ListView):
    model = CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_news.html'
    paginate_by = 25


class RelevantNews(ListView):
    model = CnnNews
    context_object_name = 'news_collection'
    template_name = 'cnn_news.html'
    paginate_by = 25

    def get_queryset(self):
        google_trends = GoogleTrendsAtom.objects.values_list('title', flat=True)
        queryset = CnnNews.objects.none()
        for trend in google_trends:
            relevant_news = CnnNews.objects.filter(title__icontains=trend)
            if relevant_news:
                queryset = queryset | relevant_news
        return queryset
