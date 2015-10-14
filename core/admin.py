from datetime import datetime
from django.contrib import admin
from core.models import Page, HelpPage


class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "heading", "content")
    ordering = ["name"]
    search_fields = ("name",)

    fieldsets = [
        (None, {"fields": ["name", "title", "heading", "content"]}),
    ]


class HelpPageAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "heading", "content", "is_live")
    ordering = ["name"]
    search_fields = ("name",)

    fieldsets = [
        ("Content", {"fields": ["name", "heading", "content"]}),
        ("Promotion", {"fields": ["slug", "title" "show", "description"]}),
        ("Settings", {"fields": ["activate", "deactivate"]}),
    ]

    def is_live(self, obj):
        return (obj.activate is not None and obj.activate > datetime.now()) and \
               (obj.deactivate is None or obj.deactivate < datetime.now())
    is_live.short_description = 'Active'

admin.site.register(Page, PageAdmin)
admin.site.register(HelpPage, HelpPageAdmin)