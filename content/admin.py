from django.contrib import admin, messages
from content.models import Journey, Module, Level, LevelQuestion, LevelQuestionOption, JourneyModuleRel, \
    HarambeeQuestionAnswer, HarambeeeQuestionAnswerTime, HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel
from forms import LevelForm, LevelQuestionForm, OptionsInlineFormset
from my_auth.filters import HarambeeFilter
from content.filters import HarambeeLevelFilter, ModuleLevelFiltler, ModuleFilter
from django.utils import timezone


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


class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "order", "question_order", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "text", "module", "order", "question_order"]}),
    ]

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

    actions = ['custom_delete']

    def get_actions(self, request):
        actions = super(LevelAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def custom_delete(self, request, obj):
        for o in obj.all():
            if o.module.start_date:
                if o.module.start_date < timezone.now():
                    messages.error(request, "Cannot delete a level that is linked to a live module.")
                    continue
            messages.info(request, "Level '%s' deleted." % o.name)
            o.delete()

    custom_delete.short_description = 'Delete selected levels'

    def delete_model(self, request, obj):
        if obj.module.start_date:
            if obj.module.start_date < timezone.now():
                messages.error(request, "Cannot delete a level that is linked to a live module.")
                return False
        obj.delete()

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.module.start_date:
                if obj.module.start_date < timezone.now():
                    return False
        return True


class LevelQuestionOptionInline(admin.StackedInline):
    model = LevelQuestionOption
    extra = 1
    fields = ("name", "question", "content", "correct")
    readonly_fields = ('name',)
    formset = OptionsInlineFormset


class LevelQuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "order", "question_content", "is_active")

    fieldsets = [
        (None, {"fields": ["name", "level", "order", "question_content", "notes", "image"]}),
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

    actions = ['custom_delete']

    def get_actions(self, request):
        actions = super(LevelQuestionAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def custom_delete(self, request, obj):
        for o in obj.all():
            if o.level.module.start_date:
                if o.level.module.start_date < timezone.now():
                    messages.error(request, "Cannot delete a question in a level that is linked to a live module.")
                    continue
            messages.info(request, "Question '%s' deleted." % o.name)
            o.delete()

    custom_delete.short_description = 'Delete selected questions'

    def delete_model(self, request, obj):
        if obj.level.module.start_date:
            if obj.level.module.start_date < timezone.now():
                messages.error(request, "Cannot delete a question in a level that is linked to a live module.")
                return False
        obj.delete()

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.level.module.start_date:
                if obj.level.module.start_date < timezone.now():
                    return False
        return True


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


class HarambeeJourneyModuleRelAdmin(admin.ModelAdmin):
    list_display = ("harambee", "get_module_name", "state", "last_active", "date_started", "date_completed",)

    fieldsets = [
        (None, {"fields": ["harambee", "state", "last_active", "date_started",
                           "date_completed"]}),
    ]

    readonly_fields = ("harambee", "journey_module_rel", "last_active", "date_started", "date_completed")

    search_fields = ("harambee__first_name", "harambee__last_name", "journey_module_rel__module__name")

    list_filter = [HarambeeFilter, ModuleFilter, "state"]

    def has_add_permission(self, request):
        return False

    def get_module_name(self, obj):
        return obj.journey_module_rel.module.name
    get_module_name.short_description = "Module"


class HarambeeJourneyModuleLevelRelAdmin(admin.ModelAdmin):
    list_display = ("get_harembee", "get_module_name", "level", "state", "level_attempt", "level_passed",
                    "last_active", "date_started", "date_completed",)

    fieldsets = [
        (None, {"fields": ["level", "level_attempt", "state", "level_passed", "current_question", "last_active",
                           "date_started", "date_completed"]}),
    ]

    readonly_fields = ("harambee_journey_module_rel", "level", "level_passed", "date_started", "date_completed",
                       "last_active", "level_attempt", "current_question",)

    list_filter = [HarambeeLevelFilter, ModuleLevelFiltler, "level", "state"]

    def has_add_permission(self, request):
        return False

    def get_harembee(self, obj):
        return obj.harambee_journey_module_rel.harambee

    def get_module_name(self, obj):
        return obj.harambee_journey_module_rel.journey_module_rel.module.name
    get_module_name.short_description = "Module"


admin.site.register(Journey, JourneyAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(LevelQuestion, LevelQuestionAdmin)
admin.site.register(HarambeeQuestionAnswer, HarambeeQuestionAnswerAdmin)
admin.site.register(HarambeeeQuestionAnswerTime, HarambeeeQuestionAnswerTimeAdmin)
admin.site.register(HarambeeJourneyModuleRel, HarambeeJourneyModuleRelAdmin)
admin.site.register(HarambeeJourneyModuleLevelRel, HarambeeJourneyModuleLevelRelAdmin)