from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'harambee.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'harambee.misc_views.welcome', name='misc.welcome'),
    url(r'^why_id/$', 'harambee.misc_views.why_id', name='misc.why_id'),
    url(r'^terms/$', 'harambee.misc_views.terms', name='misc.terms'),
    url(r'^contact/$', 'harambee.misc_views.contact', name='misc.contact'),
    url(r'^about/$', 'harambee.misc_views.about', name='misc.about'),

    url(r'^join/$', 'harambee.auth_views.join', name='auth.join'),
    url(r'^login/$', 'harambee.auth_views.login', name='auth.login'),
    url(r'^forgot_pin/$', 'harambee.auth_views.forgot_pin', name='auth.forgot_pin'),
    url(r'^send_pin/$', 'harambee.auth_views.send_pin', name='auth.send_pin'),

]
