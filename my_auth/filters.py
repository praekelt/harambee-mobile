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
            return queryset.filter(harambee__id=self.value)
