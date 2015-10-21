from django.contrib import admin
from content.models import Journey, Module, Level, LevelQuestion, LevelQuestionOption, JourneyModuleRel
from forms import LevelForm, LevelQuestionForm, QuestionInlineFormset, OptionsInlineFormset


class CourseModuleInline(admin.TabularInline):
    model = JourneyModuleRel
    extra = 1


class JourneyAdmin(admin.ModelAdmin):
    list_display = ("name", "show_menu", "start_date", "end_date",)
    ordering = ["slug"]
    search_fields = ("slug",)

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "image"]}),
        ("Promotion", {"fields": ["slug", "title", "show_menu", "search", "colour"]}),
        ("Settings", {"fields": ["start_date", "end_date"]}),
    ]

    inlines = (CourseModuleInline,)


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "get_journeys", "accessibleTo", "minimum_questions", "minimum_percentage",
                    "start_date", "end_date", "publish_date")

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "end_text"]}),
        ("Promotion", {"fields": ["accessibleTo", "show_recommended", "slug", "title", "show_menu",
                                  "search"]}),
        ("Settings", {"fields": ["minimum_questions", "minimum_percentage", "store_data_per_user", "start_date",
                                 "end_date"]}),
    ]

    inlines = (CourseModuleInline,)

    def get_journeys(self, object):
        journeys = object.journeys.all()

        journeys_list = ""

        for j in journeys:
            journeys_list += j.name + "\n"

        return journeys_list
    get_journeys.short_description = "Journeys"


class LevelQuestionInline(admin.StackedInline):
    model = LevelQuestion
    extra = 1
    fields = ("name", "description", "order", "level", "question_content", "answer_content", "notes", "image")
    formset = QuestionInlineFormset


class LevelAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "module", "question_order", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "text", "module", "order", "question_order"]}),
    ]

    inlines = (LevelQuestionInline,)

    ordering = ["module__name", "name"]
    list_filter = ("module",)

    form = LevelForm
    add_form = LevelForm

    def is_active(self, object):
        return object.is_active()
    is_active.short_description = "Active"




class LevelQuestionOptionInline(admin.StackedInline):
    model = LevelQuestionOption
    extra = 1
    fields = ("name", "question", "content", "correct")
    formset = OptionsInlineFormset


class LevelQuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "level", "question_content", "answer_content",)

    fieldsets = [
        (None, {"fields": ["name", "description", "level", "order", "question_content", "answer_content", "notes",
                           "image"]}),
    ]

    inlines = (LevelQuestionOptionInline,)

    ordering = ["level", "name"]
    list_filter = ("level",)

    form = LevelQuestionForm
    add_form = LevelQuestionForm


class LevelQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "question", "correct")

    fieldsets = [
        (None, {"fields": ["name", "question", "content", "correct"]}),
    ]

    ordering = ["question", "name"]
    list_filter = ("question",)


admin.site.register(Journey, JourneyAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(LevelQuestion, LevelQuestionAdmin)
admin.site.register(LevelQuestionOption, LevelQuestionOptionAdmin)