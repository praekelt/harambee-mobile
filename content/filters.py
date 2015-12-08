from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from my_auth.models import Harambee
from content.admin import JourneyModuleRel


class HarambeeLevelFilter(admin.SimpleListFilter):
    title = _('User')
    parameter_name = 'harambee'

    def lookups(self, request, model_admin):
        return [(x.id, x.first_name + ' ' + x.last_name) for x
                in Harambee.objects.all().order_by('first_name', 'last_name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(harambee_journey_module_rel__harambee__id=self.value)


class ModuleFilter(admin.SimpleListFilter):
    title = _('Module')
    parameter_name = 'module'

    def lookups(self, request, model_admin):
        return [(x.id, x.module.name) for x in JourneyModuleRel.objects.all().order_by('module__name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(journey_module_rel__id=self.value)


class ModuleLevelFiltler(admin.SimpleListFilter):
    title = _('Module')
    parameter_name = 'module'

    def lookups(self, request, model_admin):
        return [(x.id, x.module.name) for x in JourneyModuleRel.objects.all().order_by('module__name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(harambee_journey_module_rel__journey_module_rel__id=self.value)
