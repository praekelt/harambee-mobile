from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from harambee.views import PageView, HelpPageView, LoginView, JoinView, ProfileView, MenuView, \
    CompletedModuleView, HomeView, ModuleIntroView, ModuleHomeView, JourneyHomeView, ForgotPinView, \
    ChangePinView, ChangeMobileNumberView, LevelIntroView, ModuleEndView, \
    LevelEndView, QuestionView, RightView, WrongView, IntroView, HelpView, LogoutView, CustomSearchView


urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),

    url(r'^menu/$', MenuView.as_view(), name='misc.menu'),

    url(r'^$', RedirectView.as_view(url="/welcome", permanent=True)),

    url(r'^join/$', JoinView.as_view(), name='auth.join'),
    url(r'^login/$', LoginView.as_view(), name='auth.login'),
    url(r'^logout/$', LogoutView.as_view(), name='auth.logout'),
    url(r'^forgot_pin/$', ForgotPinView.as_view(), name='auth.forgot_pin'),
    url(r'^profile/$', ProfileView.as_view(), name='auth.profile'),
    url(r'^change_number/$', ChangeMobileNumberView.as_view(), name='auth.change_number'),
    url(r'^change_pin/$', ChangePinView.as_view(), name='auth.change_pin'),

    url(r'^intro/$', IntroView.as_view(), name='misc.intro'),
    url(r'^help/$', HelpView.as_view(), name='misc.help'),

    url(r'^home/$', HomeView.as_view(), name='content.home'),
    url(r'^journey_home/(?P<slug>[-\w]+)/$', JourneyHomeView.as_view(), name='content.journey_home'),
    url(r'^completed_modules/$', CompletedModuleView.as_view(), name='content.completed_modules'),
    url(r'^module_intro/(?P<slug>[-\w]+)/$', ModuleIntroView.as_view(), name='content.module_intro'),
    url(r'^module_home/(?P<slug>[-\w]+)/$', ModuleHomeView.as_view(), name='content.module_home'),
    url(r'^module_end/(?P<slug>[-\w]+)/$', ModuleEndView.as_view(), name='content.module_end'),
    url(r'^level_intro/(?P<pk>[0-9]+)/$', LevelIntroView.as_view(), name='content.level_intro'),
    url(r'^level_end/(?P<pk>[0-9]+)/$', LevelEndView.as_view(), name='content.level_end'),
    url(r'^question/(?P<pk>[0-9]+)/$', QuestionView.as_view(), name='content.question'),
    url(r'^right/(?P<pk>[0-9]+)/$', RightView.as_view(), name='content.right'),
    url(r'^wrong/(?P<pk>[0-9]+)/$', WrongView.as_view(), name='content.wrong'),

    url(r'^search/', CustomSearchView()),
    # url(r'^search/', include('haystack.urls')),

    url(r'^(?P<slug>[-\w]+)/$', PageView.as_view()),
    url(r'^help/(?P<slug>[-\w]+)/$', HelpPageView.as_view()),

]
