from django.contrib import admin
from communication.models import Sms
from my_auth.filters import HarambeeFilter
from django.http import HttpResponseRedirect


class SmsAdmin(admin.ModelAdmin):
    list_display = ('harambee', 'message', 'sent', 'date_created', 'time_sent')
    fieldsets = [
        ('SMS', {'fields': ['harambee', 'message', 'sent']}),
    ]

    search_fields = ('harambee__first_name', 'harambee__last_name', 'harambee__username',)
    list_filter = (HarambeeFilter, 'sent')

    def has_add_permission(self, request):
        return False
    readonly_fields = ('sent', )


admin.site.register(Sms, SmsAdmin)
