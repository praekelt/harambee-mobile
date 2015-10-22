from django.contrib import admin
from content.models import Journey, Module, Level, LevelQuestion, LevelQuestionOption


class LevelQuestionInline(admin.StackedInline):
    model = LevelQuestion
    extra = 1
    fields = ("name", "description", "order", "level", "question_content", "answer_content", "notes", "image")


class LevelQuestionOptionInline(admin.StackedInline):
    model = LevelQuestionOption
    extra = 1
    fields = ("name", "question", "order", "content", "correct")


class JourneyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "show_menu", "title", "intro_text", "search", "start_date", "end_date")
    ordering = ["slug"]
    search_fields = ("slug",)

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "image"]}),
        ("Promotion", {"fields": ["slug", "title", "show_menu", "search", "colour"]}),
        ("Settings", {"fields": ["start_date", "end_date"]}),
    ]


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "intro_text", "end_text", "get_journeys", "accessibleTo", "show_recommended", "slug",
                    "title", "show_menu", "search", "minimum_questions", "minimum_percentage", "store_data_per_user",
                    "start_date", "end_date", "publish_date")

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "end_text"]}),
        ("Promotion", {"fields": ["journeys", "accessibleTo", "show_recommended", "slug", "title", "show_menu",
                                  "search"]}),
        ("Settings", {"fields": ["minimum_questions", "minimum_percentage", "store_data_per_user", "start_date",
                                 "end_date"]}),
    ]

    def get_journeys(self, module):
        journeys = module.journeys.all()

        journeys_list = ""

        for j in journeys:
            journeys_list += j.name + "\n"

        return journeys_list

    get_journeys.short_description = "Journeys"


class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "text", "module", "question_order",)

    fieldsets = [
        (None, {"fields": ["name", "text", "module", "question_order"]}),
    ]

    inlines = (LevelQuestionInline,)


class LevelQuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "order", "level", "question_content", "answer_content", "notes", "image")

    fieldsets = [
        (None, {"fields": ["name", "description", "order", "level", "question_content", "answer_content", "notes",
                           "image"]}),
    ]

    inlines = (LevelQuestionOptionInline,)


class LevelQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "question", "order", "content", "correct")

    fieldsets = [
        (None, {"fields": ["name", "question", "order", "content", "correct"]}),
    ]


admin.site.register(Journey, JourneyAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(LevelQuestion, LevelQuestionAdmin)
admin.site.register(LevelQuestionOption, LevelQuestionOptionAdmin)