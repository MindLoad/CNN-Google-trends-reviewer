from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """ Base model """

    title = models.CharField(max_length=500)
    url = models.URLField()
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class GoogleTrendsAtomManager(models.Manager):
    """ Custom manager for GoogleTrendsAtom """
    def add_trend(self, title, url, updated):
        record = self.create(title=title, url=url, updated=updated)
        return record


class GoogleTrendsAtom(BaseModel):
    """ Google Trends Model """

    updated = models.DateTimeField()

    objects = GoogleTrendsAtomManager()

    class Meta(BaseModel.Meta):
        ordering = ['-updated']
        verbose_name_plural = 'Google Trends'


class CnnChannelsManager(models.Manager):
    """ Custom manager for CnnRssList """
    def add_channel(self, url):
        title = url.split('/')[-1]
        record = self.create(title=title, url=url)
        return record


class CnnChannels(BaseModel):
    """ List of available CNN channels """

    objects = CnnChannelsManager()

    class Meta(BaseModel.Meta):
        ordering = ['created']
        verbose_name_plural = 'CNN Channels'


class CnnNewsManager(models.Manager):
    """ Custom manager for CnnNews """
    def add_news(self, channel, title, url, posted):
        record = self.create(channel=channel, title=title, url=url, posted=posted)
        return record


class CnnNews(BaseModel):
    """ CNN news from CNN channels """

    channel = models.ForeignKey(CnnChannels, on_delete=models.CASCADE)
    posted = models.DateTimeField(blank=True)

    objects = CnnNewsManager()

    class Meta(BaseModel.Meta):
        ordering = ['-created']
        verbose_name_plural = 'CNN News'
