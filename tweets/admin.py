from django.contrib import admin
from tweets.models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    # sorting method
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )
