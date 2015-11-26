from django.utils import timezone
from django.contrib import admin
from core.models import Page, HelpPage


class PageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "heading", "content")
    ordering = ["slug"]
    search_fields = ("slug",)

    fieldsets = [
        (None, {"fields": ["slug", "title", "heading", "content"]}),
    ]


class HelpPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "heading", "content", "is_live")
    ordering = ["slug"]
    search_fields = ("slug",)

    fieldsets = [
        ("Content", {"fields": ["slug", "title", "heading", "content"]}),
        ("Promotion", {"fields": ["show", "description"]}),
        ("Settings", {"fields": ["activate", "deactivate"]}),
    ]

    def is_live(self, obj):
        return (obj.activate is not None and obj.activate > timezone.now()) and \
               (obj.deactivate is None or obj.deactivate < timezone.now())
    is_live.short_description = 'Active'

admin.site.register(Page, PageAdmin)
admin.site.register(HelpPage, HelpPageAdmin)