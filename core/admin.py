from django.contrib import admin

from core.models import Project, UserProfile

# Register your models here.

admin.site.register(Project)
admin.site.register(UserProfile)
