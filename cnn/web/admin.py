from django.contrib import admin

from .models import GoogleTrendsAtom, CnnChannels, CnnNews

admin.site.register(CnnChannels)


@admin.register(GoogleTrendsAtom)
class GoogleTrendsAtomAdmin(admin.ModelAdmin):
    """ Google Trends model """

    fields = ['title', 'url', 'updated']
    list_display = ('title', 'url', 'updated')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_per_page = 25


@admin.register(CnnNews)
class CnnNewsAdmin(admin.ModelAdmin):
    """ CNN News model """

    fields = ['channel', 'title', 'url', 'posted']
    list_display = ('title', 'channel')
    list_display_links = ('title',)
    list_filter = ('channel',)
    search_fields = ('title',)
    list_per_page = 25
