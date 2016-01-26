from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from my_auth.models import Harambee
from content.models import JourneyModuleRel, HarambeeJourneyModuleRel
from django.utils import timezone
from datetime import timedelta


class HarambeeFilter(admin.SimpleListFilter):
    title = _('User')
    parameter_name = 'harambee'

    def lookups(self, request, model_admin):
        return [(x.id, x.first_name + ' ' + x.last_name) for x
                in Harambee.objects.all().order_by('first_name', 'last_name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(harambee__id=self.value())


class HarambeeActiveStatusFilter(admin.SimpleListFilter):
    title = _('Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [('active', 'Active'), ('inactive', 'Inactive')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            if self.value() == 'active':
                now = timezone.now()
                yesterday = timezone.now() - timedelta(hours=24)
                harambee_list = Harambee.objects.filter(last_login__gt=yesterday, last_login__lt=now)\
                    .values_list('id', flat=True)
                return queryset.filter(id__in=harambee_list)
            else:
                two_weeks_ago = timezone.now() - timedelta(days=14)
                harambee_list = Harambee.objects.filter(last_login__lt=two_weeks_ago)
                return queryset.filter(id__in=harambee_list)


class HaramabeeActiveInModule(admin.SimpleListFilter):
    title = _('Active In Module')
    parameter_name = 'act_mod'

    def lookups(self, request, model_admin):
        return [(x.id, x.module.name) for x in JourneyModuleRel.objects.all().order_by('module__name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            harambee_list = HarambeeJourneyModuleRel.objects\
                .filter(journey_module_rel__id=self.value(), state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
                .distinct('harambee')\
                .values_list('harambee__id', flat=True)
            return queryset.filter(id__in=harambee_list)


class HarambeeCompletedModule(admin.SimpleListFilter):
    title = _('Completed Module')
    parameter_name = 'comp_mod'

    def lookups(self, request, model_admin):
        return [(x.id, x.module.name) for x in JourneyModuleRel.objects.all().order_by('module__name')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            harambee_list = HarambeeJourneyModuleRel.objects\
                .filter(journey_module_rel__id=self.value(), state=HarambeeJourneyModuleRel.MODULE_COMPLETE)\
                .distinct('harambee')\
                .values_list('harambee__id', flat=True)
            return queryset.filter(id__in=harambee_list)