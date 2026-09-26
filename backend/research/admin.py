from django.contrib import admin

from .models import Item, ResearchRun


@admin.register(ResearchRun)
class ResearchRunAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("topic",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "source", "title", "domain", "published_at")
    list_filter = ("source",)
    search_fields = ("title", "domain", "url")
