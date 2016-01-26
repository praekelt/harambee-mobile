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

    readonly_fields = ('sent', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.sent:
                return ('harambee', 'message', 'sent')
        return super(SmsAdmin, self).get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.sent:
                return False
        return True

    def get_actions(self, request):
        actions = super(SmsAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(Sms, SmsAdmin)
