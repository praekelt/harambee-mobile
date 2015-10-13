from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),

    url(r'^menu/$', 'harambee.core_views.menu', name='misc.menu'),
    url(r'^search/$', 'harambee.core_views.search', name='misc.search'),
    url(r'^search_results/$', 'harambee.core_views.search_results', name='misc.search_results'),

    url(r'^$', 'harambee.misc_views.welcome', name='misc.welcome'),
    url(r'^why_id/$', 'harambee.misc_views.why_id', name='misc.why_id'),
    url(r'^terms/$', 'harambee.misc_views.terms', name='misc.terms'),
    url(r'^contact/$', 'harambee.misc_views.contact', name='misc.contact'),
    url(r'^about/$', 'harambee.misc_views.about', name='misc.about'),
    url(r'^intro/$', 'harambee.misc_views.intro', name='misc.intro'),
    url(r'^help/$', 'harambee.misc_views.main_help', name='misc.help'),
    url(r'^help_page/(?P<page_id>\d+)$', 'harambee.misc_views.help_page', name='misc.help_page'),

    url(r'^join/$', 'harambee.auth_views.join', name='auth.join'),
    url(r'^login/$', 'harambee.auth_views.login', name='auth.login'),
    url(r'^forgot_pin/$', 'harambee.auth_views.forgot_pin', name='auth.forgot_pin'),
    url(r'^send_pin/$', 'harambee.auth_views.send_pin', name='auth.send_pin'),
    url(r'^profile/$', 'harambee.auth_views.profile', name='auth.profile'),
    url(r'^change_number/$', 'harambee.auth_views.change_number', name='auth.change_number'),
    url(r'^change_pin/$', 'harambee.auth_views.change_pin', name='auth.change_pin'),

    url(r'^home/$', 'harambee.content_views.home', name='content.home'),
    url(r'^journey_home/(?P<journey_id>\d+)/(?P<page_count>\d+)$', 'harambee.content_views.journey_home',
        name='content.journey_home'),
    url(r'^completed_modules/(?P<page_count>\d+)$', 'harambee.content_views.completed_modules',
        name='content.completed_modules'),
    url(r'^module_intro/(?P<module_id>\d+)$', 'harambee.content_views.module_intro', name='content.module_intro'),
    url(r'^module_home/(?P<module_id>\d+)$', 'harambee.content_views.module_home', name='content.module_home'),

]
