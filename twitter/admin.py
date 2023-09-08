from django.contrib import admin

from .models import Tweets, TwitterAccount

# Register your models here.
admin.site.register(Tweets)
admin.site.register(TwitterAccount)
