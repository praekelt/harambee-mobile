from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from my_auth.forms import HarambeeChangeForm, HarambeeCreationForm, SystemAdministratorChangeForm, \
    SystemAdministratorCreationForm
from my_auth.models import Harambee, SystemAdministrator


class HarambeeAdmin(UserAdmin):
    # The forms to add and change user instances
    form = HarambeeChangeForm
    add_form = HarambeeCreationForm
    list_max_show_all = 1000
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("username", "first_name", "last_name", "mobile", "email", "lps", "candidate_id")
    list_filter = ("first_name", "last_name", "mobile")
    search_fields = ("last_name", "first_name", "username")
    ordering = ("last_name", "first_name", "last_login")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name",
                                      "email", "mobile", "lps", "candidate_id")}),
        ("Access", {"fields": ("username", "password",
                               "is_active", "unique_token")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name", "mobile", "lps", "candidate_id")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
    )


class SystemAdministratorAdmin(UserAdmin):
    # The forms to add and change user instances
    form = SystemAdministratorChangeForm
    add_form = SystemAdministratorCreationForm

    list_display = ("username", "last_name", "first_name")
    search_fields = ("last_name", "first_name", "username")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name", "email",
                                      "mobile")}),
        ("Access", {"fields": ("username", "password", "is_active")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
    )

admin.site.register(Harambee, HarambeeAdmin)
admin.site.register(SystemAdministrator, SystemAdministratorAdmin)
