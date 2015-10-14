from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from harambee.views import PageView, HelpPageView, LoginView, JoinView, ProfileView, MenuView, \
    CompletedModuleView, HomeView, ModuleIntroView, ModuleHomeView, JourneyHomeView, SearchView, \
    SearchResultView, ForgotPinView, ChangePinView, ChangeMobileNumberView, LevelIntroView

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),

    url(r'^menu/$', MenuView.as_view(), name='misc.menu'),
    url(r'^search/$', SearchView.as_view(), name='misc.search'),
    url(r'^search_results/$', SearchResultView.as_view(), name='misc.search_results'),

    url(r'^$', RedirectView.as_view(url="/welcome")),

    url(r'^join/$', JoinView.as_view(), name='auth.join'),
    url(r'^login/$', LoginView.as_view(), name='auth.login'),
    url(r'^forgot_pin/$', ForgotPinView.as_view(), name='auth.forgot_pin'),
    url(r'^profile/(?P<pk>[0-9]+)/$', ProfileView.as_view(), name='auth.profile'),
    url(r'^change_number/$', ChangeMobileNumberView.as_view(), name='auth.change_number'),
    url(r'^change_pin/$', ChangePinView.as_view(), name='auth.change_pin'),

    url(r'^home/$', HomeView.as_view(), name='content.home'),
    url(r'^journey_home/(?P<slug>[-\w]+)/$', JourneyHomeView.as_view(), name='content.journey_home'),
    url(r'^completed_modules/$', CompletedModuleView.as_view(), name='content.completed_modules'),
    url(r'^module_intro/(?P<slug>[-\w]+)/$', ModuleIntroView.as_view(), name='content.module_intro'),
    url(r'^module_home/(?P<slug>[-\w]+)/$', ModuleHomeView.as_view(), name='content.module_home'),
    url(r'^level_intro/(?P<slug>[-\w]+)/$', LevelIntroView.as_view(), name='content.level_intro'),

    url(r'^(?P<slug>[-\w]+)/$', PageView.as_view()),
    url(r'^help/(?P<slug>[-\w]+)/$', HelpPageView.as_view()),

]
