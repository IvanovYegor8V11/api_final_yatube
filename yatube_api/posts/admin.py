from django.contrib import admin

from .models import Post, Group, Comment, Follow


@admin.register(Post, Group, Comment, Follow)
class BlogAdmin(admin.ModelAdmin):
    ...
