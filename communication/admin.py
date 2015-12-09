from django.contrib import admin
from communication.models import Sms
from my_auth.filters import HarambeeFilter


class SmsAdmin(admin.ModelAdmin):
    list_display = ('harambee', 'message', 'sent', 'time_sent')
    fieldsets = [
        ('SMS', {'fields': ['harambee', 'message', 'sent', 'time_sent']}),
    ]

    readonly_fields = ('harambee', 'message', 'sent', 'date_created', 'time_sent',)

    search_fields = ('harambee__first_name', 'harambee__last_name', 'harambee__username',)
    list_filter = (HarambeeFilter, 'sent')

    def has_add_permission(self, request):
        return False


admin.site.register(Sms, SmsAdmin)
