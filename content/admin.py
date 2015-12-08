from django.contrib import admin
from content.models import Journey, Module, Level, LevelQuestion, LevelQuestionOption, JourneyModuleRel, \
    HarambeeQuestionAnswer, HarambeeeQuestionAnswerTime
from forms import LevelForm, LevelQuestionForm, QuestionInlineFormset, OptionsInlineFormset


class CourseModuleInline(admin.TabularInline):
    model = JourneyModuleRel
    extra = 1


class JourneyAdmin(admin.ModelAdmin):
    list_display = ("name", "show_menu", "start_date", "end_date", "is_active")
    ordering = ["slug"]
    search_fields = ("slug",)

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "image"]}),
        ("Promotion", {"fields": ["slug", "title", "show_menu", "search", "colour"]}),
        ("Settings", {"fields": ["start_date", "end_date"]}),
    ]

    inlines = (CourseModuleInline,)

    def is_active(self, object):
        if object.is_active():
            return "<img src='/static/admin/img/icon-yes.gif' alt='True'>"
        else:
            return "<img src='/static/admin/img/icon-no.gif' alt='False'>"
    is_active.short_description = "Live"
    is_active.allow_tags = True


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "get_journeys", "accessibleTo", "minimum_questions", "minimum_percentage",
                    "start_date", "end_date", "publish_date", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "intro_text", "end_text", "image"]}),
        ("Promotion", {"fields": ["accessibleTo", "show_recommended", "slug", "title", "show_menu",
                                  "search"]}),
        ("Settings", {"fields": ["minimum_questions", "minimum_percentage", "store_data_per_user", "start_date",
                                 "end_date"]}),
    ]

    inlines = (CourseModuleInline,)

    search_fields = ("name", )

    def is_active(self, object):
        if object.is_active():
            return "<img src='/static/admin/img/icon-yes.gif' alt='True'>"
        else:
            return "<img src='/static/admin/img/icon-no.gif' alt='False'>"
    is_active.short_description = "Live"
    is_active.allow_tags = True

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
    fields = ("name", "description", "order", "level", "question_content", "notes", "image")
    formset = QuestionInlineFormset


class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "order", "question_order", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "text", "module", "order", "question_order"]}),
    ]

    inlines = (LevelQuestionInline,)

    ordering = ["module__name", "name"]
    list_filter = ("module",)

    form = LevelForm
    add_form = LevelForm

    def is_active(self, object):
        if object.is_active():
            return "<img src='/static/admin/img/icon-yes.gif' alt='True'>"
        else:
            return "<img src='/static/admin/img/icon-no.gif' alt='False'>"
    is_active.short_description = "Live"
    is_active.allow_tags = True


class LevelQuestionOptionInline(admin.StackedInline):
    model = LevelQuestionOption
    extra = 1
    fields = ("name", "question", "content", "correct")
    formset = OptionsInlineFormset


class LevelQuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "order", "question_content", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "description", "level", "order", "question_content", "notes", "image"]}),
    ]

    inlines = (LevelQuestionOptionInline,)

    ordering = ["level", "name"]
    list_filter = ("level",)
    search_fields = ("name",)

    form = LevelQuestionForm
    add_form = LevelQuestionForm

    def is_active(self, object):
        if len(object.levelquestionoption_set.all()) >= 2:
            return "<img src='/static/admin/img/icon-yes.gif' alt='True'>"
        else:
            return "<img src='/static/admin/img/icon-no.gif' alt='False'>"
    is_active.short_description = "Live"
    is_active.allow_tags = True


class HarambeeQuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ("harambee", "question", "option_selected", "date_answered", "is_correct",)

    fieldsets = [
        (None, {"fields": ["harambee", "question", "option_selected", "date_answered"]}),
    ]

    ordering = ("harambee",)
    list_filter = ["harambee", "question", "option_selected"]
    search_fields = ("harambee",)

    readonly_fields = ("harambee", "question", "option_selected", "date_answered",)

    def has_add_permission(self, request):
        return False

    def is_correct(self, object):
        if object.is_correct():
            return "<img src='/static/admin/img/icon-yes.gif' alt='True'>"
        else:
            return "<img src='/static/admin/img/icon-no.gif' alt='False'>"
    is_correct.short_description = "Correct"
    is_correct.allow_tags = True


class HarambeeeQuestionAnswerTimeAdmin(admin.ModelAdmin):
    list_display = ("harambee", "question", "answer_time",)

    fieldsets = [
        (None, {"fields": ["harambee", "question"]}),
    ]

    readonly_fields = ("harambee", "question",)

    def has_add_permission(self, request):
        return False

    def answer_time(self, object):
        return object.answer_time_minutes()
    answer_time.short_description = "Time taken to answer"


admin.site.register(Journey, JourneyAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(LevelQuestion, LevelQuestionAdmin)
admin.site.register(HarambeeQuestionAnswer, HarambeeQuestionAnswerAdmin)
admin.site.register(HarambeeeQuestionAnswerTime, HarambeeeQuestionAnswerTimeAdmin)