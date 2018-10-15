from django.views.generic import ListView
from django.db.models import Subquery

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
        google_trends = GoogleTrendsAtom.objects.all()
        return CnnNews.objects.filter(title__icontains=Subquery(google_trends.values('title')))
