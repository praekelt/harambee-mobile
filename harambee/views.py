from __future__ import division
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, FormView, ListView, TemplateView
from django.contrib.auth import logout
from django.contrib import messages
from my_auth.models import HarambeeLog
from django.shortcuts import HttpResponseRedirect, redirect, render
from core.models import Page, HelpPage
from content.models import Journey, Module, Level, HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, \
    JourneyModuleRel, HarambeeState, LevelQuestionOption, HarambeeQuestionAnswer, HarambeeeQuestionAnswerTime
from harambee.forms import *
from haystack.views import SearchView
from django.utils import timezone
from django.db.models import Count
from functools import wraps
from helper_functions import get_menu_journeys, get_new_modules, get_journey_data, \
    get_harambee_completed_modules, get_harambee_active_levels,\
    get_harambee_locked_levels, get_level_data, get_module_data, get_module_data_from_queryset,\
    unlock_first_level, has_completed_all_modules, get_journey_module, get_harambee_journey_completed_modules,\
    get_active_module_data_by_journey, get_completed_active_module_data_by_journey
from rolefit.communication import *
from random import randint, choice
from django.db.models import Q
import httplib2
from django.core.mail import mail_managers
from communication.tasks import send_immediate_sms_task
from communication.models import Sms

PAGINATE_BY = 5


def save_user_session(request, user):

    request.session["user"] = {}
    request.session["user"]["id"] = user.id
    request.session["user"]["name"] = user.first_name

    #check if it's user first time logging in
    if not user.last_login:
        user.send_sms('#HarambeeLearning. Congratulations on registering for Harambee4work.mobi and taking the 1st step'
                      ' on your journey to employment!')

    # update last login date
    user.last_login = timezone.now()
    user.save()


def harambee_login_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if "user" not in request.session.keys():
            return redirect("/login")
        return f(request, user=request.session["user"], *args, **kwargs)
    return wrap


def check_if_logged(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if request.session.get('user'):
            return HttpResponseRedirect('/home/')
        return f(request, *args, **kwargs)
    return wrap


def admin_login_required(f):
    @wraps(f)
    def wrap(request, *arg, **kwargs):
        if not request.user.is_authenticated():
            return redirect('/admin/login/')
        return f(request, *arg, **kwargs)
    return wrap


def get_harambee(request, context):
    user = request.session["user"]
    context["user"] = user
    return context, Harambee.objects.get(id=user["id"])


def get_harambee_state(user):
    harambee = Harambee.objects.get(username=user.username)
    try:
        state = HarambeeState.objects.get(harambee=harambee)
    except HarambeeState.DoesNotExist:
        state = HarambeeState.objects.create(harambee=harambee)

    return state


def update_state(harambee, harambee_journey_module_level_rel):
    state = get_harambee_state(harambee)
    state.active_level_rel = harambee_journey_module_level_rel
    state.save()


class PageView(DetailView):

    template_name = "misc/page.html"
    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)

        if self.kwargs.get('slug', None) == "welcome":
            self.template_name = "misc/welcome.html"

        elif self.kwargs.get('slug', None) == "no_match":
            self.template_name = "auth/no_match.html"

        elif self.kwargs.get('slug', None) == "send_pin":
            self.template_name = "auth/send_pin.html"

        if "user" in self.request.session.keys():
            context["user"] = self.request.session["user"]

        context["header_colour"] = "green-back"
        context["hide"] = True
        return context


class ContactView(FormView):

    template_name = 'misc/contact.html'
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)

        page = Page.objects.get(slug='contact')

        context['object'] = page
        return context

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        id_number = form.cleaned_data['id_number']
        mobile = form.cleaned_data['mobile']
        message = form.cleaned_data['message']

        text = 'Name: %s\nSurname: %s\nID: %s\nMobile: %s\nMessage: %s\n' % (first_name, last_name, id_number,
                                                                             mobile, message)

        mail_managers('Message', text, fail_silently=False)

        return render(self.request, 'misc/error.html',
                      {'title': 'MESSAGE SENT', 'header': 'Message Sent',
                       'message': 'Your message has been sent.'},
                      content_type='text/html')


class CustomSearchView(SearchView):

    results_per_page = PAGINATE_BY

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(CustomSearchView, self).dispatch(*args, **kwargs)

    def extra_context(self):
        extra = super(CustomSearchView, self).extra_context()

        user_id = self.request.session["user"]["id"]
        rel_id_list = list()
        if not self.results == []:
            for result in self.results:
                rel_id_list += (HarambeeJourneyModuleRel.objects
                                .filter(harambee__id=user_id, journey_module_rel__module__id=result.pk)
                                .values_list('id', flat=True))

            all_rels = HarambeeJourneyModuleRel.objects.filter(id__in=rel_id_list)
            extra["module_list"] = get_module_data_from_queryset(all_rels)

        user = self.request.session["user"]
        extra["user"] = user
        extra["header_colour"] = "green-back"
        extra["hide"] = True
        return extra


class JoinView(FormView):

    template_name = 'auth/join.html'
    form_class = JoinForm
    success_url = '/home'

    def get_context_data(self, **kwargs):
        context = super(JoinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="join")
        context["page"] = page
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        try:
            harambee = get_harambee_by_id(username)
            if not harambee:
                return HttpResponseRedirect('/no_match')
        except ValueError:
            return HttpResponseRedirect('/no_match')
        except httplib2.ServerNotFoundError:
            return render(self.request, 'misc/error.html',
                          {'title': 'SERVER UNAVAILABLE', 'header': 'ROLEFIT UNAVAILABLE',
                           'message': 'Rolefit server is currently unavailable, please try again later.'},
                          content_type='text/html')

        try:
            Harambee.objects.get(username=username)
            return HttpResponseRedirect('/login')
        except Harambee.DoesNotExist:
            # check if users mobile number exists in the database
            try:
                Harambee.objects.get(mobile=harambee['contactNo'])
                return render(self.request, 'misc/error.html',
                              {'title': 'REGISTRATION ERROR', 'header': 'Registration Error',
                               'message': 'User with mobile number [%s] already exists. Please contact the admin to '
                                          'assist you. <a href="/contact/" style="color: #0000FF;">Email Harambee.</a>'
                                          % harambee['contactNo']}, content_type='text/html')
            except Harambee.DoesNotExist:
                # check if there is a user with retrieved candidate_id
                try:
                    Harambee.objects.get(candidate_id=harambee['candidateId'])
                    # TODO: add email address
                    return render(self.request, 'misc/error.html',
                                  {'title': 'REGISTRATION ERROR', 'header': 'Registration Error',
                                   'message': 'An error occurred with your registration. Please contact the admin to '
                                              'assist you. <a "/contact/" style="color: #0000FF;">Email Harambee.</a>'},
                                  content_type='text/html')
                except Harambee.DoesNotExist:
                    try:
                        lps = get_lps(harambee['candidateId'])
                    except httplib2.ServerNotFoundError:
                        return render(self.request, 'misc/error.html',
                                      {'title': 'SERVER UNAVAILABLE', 'header': 'ROLEFIT UNAVAILABLE',
                                       'message': 'Rolefit server is currently unavailable, please try again later.'},
                                      content_type='text/html')

                    user = Harambee.objects.create(first_name=harambee['name'], last_name=harambee['surname'], lps=lps,
                                                   candidate_id=harambee['candidateId'], email=harambee['emailAddr'],
                                                   mobile=harambee['contactNo'], username=username)
                    user.set_password(raw_password=password)
                    user.save()

                    user = authenticate(
                        username=form.cleaned_data["username"],
                        password=form.cleaned_data["password"]
                    )

                    harambee = Harambee.objects.get(username=user.username)
                    save_user_session(self.request, harambee)
                    get_harambee_state(harambee)
                    return HttpResponseRedirect("/intro")


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = '/home'

    @method_decorator(check_if_logged)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(LoginView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="login")
        context["page"] = page
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(username=form.cleaned_data["username"])
        HarambeeLog.objects.create(harambee=user, date=timezone.now(), action=HarambeeLog.LOGIN)
        if not user.last_login:
            save_user_session(self.request, user)
            get_harambee_state(user)
            return HttpResponseRedirect("/intro")

        save_user_session(self.request, user)
        return super(LoginView, self).form_valid(form)


class LogoutView(View):

    def get(self, request, **kwargs):
        user = self.request.session["user"]
        harambee = Harambee.objects.get(id=user['id'])
        logout(request)
        HarambeeLog.objects.create(harambee=harambee, date=timezone.now(), action=HarambeeLog.LOGOUT)
        return HttpResponseRedirect("/")


class ForgotPinView(FormView):
    template_name = 'auth/forgot_pin.html'
    form_class = ResetPINForm
    success_url = '/send_pin'

    def get_context_data(self, **kwargs):

        context = super(ForgotPinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="forgot_pin")
        context["page"] = page
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context

    def form_valid(self, form):

        harambee = Harambee.objects.get(username=form.cleaned_data["username"])

        new_pin = self.generate_random_pin()
        harambee.set_password(new_pin)
        harambee.save()

        message = 'Your new Harambee 4 digit PIN is: %s.' % new_pin

        send_immediate_sms_task.delay(harambee, message)

        return super(ForgotPinView, self).form_valid(form)

    @staticmethod
    def generate_random_pin():
        pin = ''
        for i in range(0, 4):
            pin += str(randint(0, 9))
        return pin


class ProfileView(DetailView):

    template_name = "auth/profile.html"
    model = Harambee

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return Harambee.objects.get(id=self.request.session["user"]["id"])

    def get_context_data(self, **kwargs):

        context = super(ProfileView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


class ChangePinView(FormView):

    template_name = 'auth/change_pin.html'
    form_class = ChangePINForm
    success_url = '/successful_pin_change'

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChangePinView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):

        kwargs = super(ChangePinView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):

        context = super(ChangePinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="change_pin")
        user = self.request.session["user"]
        context["page"] = page
        context["user"] = user
        context["header_colour"] = "green-back"
        context["hide"] = False
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        user.set_password(form.cleaned_data["newPIN"])
        user.save()
        return super(ChangePinView, self).form_valid(form)


class ChangeMobileNumberView(FormView):

    template_name = 'auth/change_number.html'
    form_class = ChangeMobileNumberForm
    success_url = '/successful_mobile_change'

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChangeMobileNumberView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ChangeMobileNumberView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="change_number")
        user = self.request.session["user"]
        context["page"] = page
        context["user"] = user
        context["header_colour"] = "green-back"
        context["hide"] = False
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        user.mobile = form.cleaned_data["mobile"]
        user.save()
        #TODO: deal with a possible thrown errror
        update_mobile_number(user.candidate_id, user.mobile)
        return super(ChangeMobileNumberView, self).form_valid(form)


class IntroView(ListView):

    template_name = "misc/intro.html"
    model = Journey
    queryset = get_menu_journeys()

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(IntroView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(IntroView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="intro")
        user = self.request.session["user"]
        context["page"] = page
        context["user"] = user
        context['header_message'] = "Welcome, %s" % user["name"]
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


class MenuView(DetailView):
    model = Page
    template_name = "core/main_menu.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(MenuView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return Page.objects.get(slug="menu")

    def get_context_data(self, **kwargs):
        context = {}
        journeys = Journey.objects.filter(show_menu=True)
        user = self.request.session["user"]
        context['journeys'] = journeys
        context['user'] = user
        context['header_colour'] = 'black-back'
        context['hide'] = True
        return context


class CompletedModuleView(ListView):

    model = Module
    template_name = "content/completed_modules.html"
    paginate_by = PAGINATE_BY

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(CompletedModuleView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(CompletedModuleView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="completed_modules")
        user = self.request.session["user"]
        context["user"] = user
        context["page"] = page
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context

    def get_queryset(self):
        harambee = Harambee.objects.get(id=self.request.session['user']['id'])
        all_rel = get_harambee_completed_modules(harambee)
        module_list = list()
        for rel in all_rel:
            module_list.append(get_module_data(rel))
        return module_list


class HomeView(ListView):

    model = Journey
    template_name = "content/home.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(HomeView, self).get_context_data(**kwargs))
        user = self.request.session["user"]
        context["journeys"] = get_journey_data(harambee)
        context["user"] = user
        context['header_message'] = "Hello %s" % user["name"]
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


class JourneyHomeView(DetailView):

    template_name = "content/journey_home.html"
    model = Journey

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(JourneyHomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(JourneyHomeView, self).get_context_data(**kwargs))
        journey_slug = self.kwargs.get('slug', None)
        journey = Journey.objects.get(slug=journey_slug)
        context['journey'] = journey
        context["user"] = harambee
        new_modules = get_new_modules(journey, harambee)
        for item in new_modules:
            item.new = (timezone.now() - item.module.start_date).days < 30
        context["new_modules"] = new_modules
        context["module_list"] = get_active_module_data_by_journey(harambee, journey)
        context["completed_modules"] = get_completed_active_module_data_by_journey(harambee, journey)
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


class ModuleHomeView(TemplateView):

    model = HarambeeJourneyModuleRel
    template_name = "content/module_home.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleHomeView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        module_slug = kwargs.get('module_slug', None)
        journey_slug = kwargs.get('journey_slug', None)
        user = kwargs.get('user', None)

        journey_module_rel = get_journey_module(journey_slug, module_slug)
        if not journey_module_rel:
            return HttpResponseRedirect('/home')

        harambee = Harambee.objects.get(id=user['id'])
        try:
            rel = HarambeeJourneyModuleRel.objects.get(journey_module_rel=journey_module_rel, harambee=harambee)
            try:
                HarambeeJourneyModuleLevelRel.objects.get(harambee_journey_module_rel=rel)
            except HarambeeJourneyModuleLevelRel.DoesNotExist:
                unlock_first_level(rel)
            except HarambeeJourneyModuleLevelRel.MultipleObjectsReturned:
                pass
        except HarambeeJourneyModuleRel.DoesNotExist:
            rel = HarambeeJourneyModuleRel.objects.create(
                journey_module_rel=journey_module_rel,
                harambee=harambee,
                date_started=timezone.now())
            unlock_first_level(rel)
        return super(ModuleHomeView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "journey" in request.POST.keys() and "module" in request.POST.keys() and "level_id" in request.POST.keys():

            user = kwargs.get('user', None)
            harambee = Harambee.objects.get(id=user['id'])
            module_slug = request.POST["module"]
            journey_slug = request.POST["journey"]
            level_id = int(request.POST["level_id"])
            level = Level.objects.get(id=level_id)
            journey_module_rel = get_journey_module(journey_slug, module_slug)
            if not journey_module_rel:
                return HttpResponseRedirect(
                    '/home')
            #TODO add a check if it exists?
            harambee_journey_module_rel = HarambeeJourneyModuleRel.objects.get(journey_module_rel=journey_module_rel,
                                                                               harambee=harambee)
            all_rel = HarambeeJourneyModuleLevelRel.objects.filter(
                harambee_journey_module_rel=harambee_journey_module_rel,
                level=level).order_by("-level_attempt")

            if len(all_rel) == 0:
                harambee_journey_module_level_rel = HarambeeJourneyModuleLevelRel.objects.create(
                    harambee_journey_module_rel=harambee_journey_module_rel,
                    level=level,
                    level_attempt=1)
                update_state(harambee, harambee_journey_module_level_rel)
            else:
                try:
                    active_rel = all_rel.get(state=HarambeeJourneyModuleLevelRel.LEVEL_ACTIVE)
                except HarambeeJourneyModuleLevelRel.DoesNotExist:
                    num_attempts = all_rel.aggregate(Count('id'))['id__count']
                    active_rel = HarambeeJourneyModuleLevelRel.objects.create(
                        harambee_journey_module_rel=harambee_journey_module_rel,
                        level=level,
                        level_attempt=num_attempts+1)

                update_state(harambee, active_rel)

            return HttpResponseRedirect("/question")

        else:
            return HttpResponseRedirect(request.path)

    def get_context_data(self, **kwargs):
        context, harambee = get_harambee(self.request, super(ModuleHomeView, self).get_context_data(**kwargs))

        # TODO: Maybe move this to a method with exceptions and redirect if it fails to find the object
        module_slug = self.kwargs.get('module_slug', None)
        journey_slug = self.kwargs.get('journey_slug', None)
        journey_module_rel = get_journey_module(journey_slug, module_slug)
        if not journey_module_rel:
            return HttpResponseRedirect('/home')

        context['journey_module_rel'] = journey_module_rel
        context["user"] = harambee
        context["header_colour"] = "black-back"
        context["hide"] = False

        harambee_journey_module_rel = HarambeeJourneyModuleRel.objects.get(harambee=harambee,
                                                                           journey_module_rel=journey_module_rel)

        active_levels = get_harambee_active_levels(harambee_journey_module_rel)
        levels_data = list()
        for act_lev in active_levels:
            levels_data.append(get_level_data(act_lev))
        context["active_levels"] = levels_data
        context["locked_levels"] = get_harambee_locked_levels(harambee_journey_module_rel)
        return context


#TODO see if the user can access this screen before he should
class ModuleEndView(DetailView):

    model = JourneyModuleRel

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleEndView, self).dispatch(*args, **kwargs)

    template_name = "content/module_end.html"

    def get_context_data(self, **kwargs):

        context = super(ModuleEndView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        context["header_message"] = self.object.journey.name
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context

    def get_object(self, queryset=None):
        module_slug = self.kwargs.get('module_slug', None)
        journey_slug = self.kwargs.get('journey_slug', None)
        journey_module_rel = get_journey_module(journey_slug, module_slug)
        if not journey_module_rel:
            return HttpResponseRedirect('/home')
        return journey_module_rel


#TODO deal with levels that don't exist
class LevelIntroView(DetailView):

    model = Level
    template_name = "content/level_intro.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(LevelIntroView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(LevelIntroView, self).get_context_data(**kwargs))
        module_slug = self.kwargs.get('module_slug', None)
        journey_slug = self.kwargs.get('journey_slug', None)
        journey_module_rel = get_journey_module(journey_slug, module_slug)
        if not journey_module_rel:
            return HttpResponseRedirect(
                '/home')
        #TODO add a check if it exists?
        harambee_journey_module_rel = HarambeeJourneyModuleRel.objects.get(journey_module_rel=journey_module_rel,
                                                                           harambee=harambee)

        all_rel = HarambeeJourneyModuleLevelRel.objects.filter(
            harambee_journey_module_rel=harambee_journey_module_rel,
            level=self.object).order_by("-level_attempt")

        if len(all_rel) == 0:
            harambee_journey_module_level_rel = HarambeeJourneyModuleLevelRel.objects.create(
                harambee_journey_module_rel=harambee_journey_module_rel,
                level=self.object,
                level_attempt=1)
            update_state(harambee, harambee_journey_module_level_rel)
        else:
            try:
                active_rel = all_rel.get(state=HarambeeJourneyModuleLevelRel.LEVEL_ACTIVE)
            except HarambeeJourneyModuleLevelRel.DoesNotExist:
                num_attempts = all_rel.aggregate(Count('id'))['id__count']
                active_rel = HarambeeJourneyModuleLevelRel.objects.create(
                    harambee_journey_module_rel=harambee_journey_module_rel,
                    level=self.object,
                    level_attempt=num_attempts+1)

            update_state(harambee, active_rel)

        context["journey_module_rel"] = journey_module_rel
        context["header_message"] = journey_module_rel.journey.name
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


class LevelEndView(DetailView):

    model = HarambeeJourneyModuleLevelRel
    template_name = "content/level_end.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(LevelEndView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(LevelEndView, self).get_context_data(**kwargs))
        context["header_message"] = self.object.harambee_journey_module_rel.journey_module_rel.journey.name
        context["header_colour"] = "black-back"
        context["hide"] = False

        number_questions = self.object.level.get_num_questions()
        number_answered = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object,).\
            aggregate(Count('id'))['id__count']
        number_correct = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object,
                                                               option_selected__correct=True).\
            aggregate(Count('id'))['id__count']

        total_num_levels = self.object.harambee_journey_module_rel.journey_module_rel.module.total_levels()

        correct_percentage = 0
        if number_answered != 0:
            correct_percentage = round(number_correct * 100 / number_answered, 1)

        incorrect_percentage = round(100 - correct_percentage, 1)
        context["correct"] = correct_percentage
        context["incorrect"] = incorrect_percentage

        level_passed = self.object.harambee_journey_module_rel.harambee.check_if_level_complete(self.object)
        context["min_percent"] = self.object.harambee_journey_module_rel.harambee.get_percentage_required(self.object)
        if level_passed:
            context["message"] = "WELL DONE!"
            context["level_passed"] = True
        else:
            context["message"] = "LEVEL COMPLETED"
            context["level_passed"] = False

        next_level = Level.objects.filter(module=self.object.harambee_journey_module_rel.journey_module_rel.module,
                                          order=self.object.level.order + 1).first()
        if next_level:
            context['next_level'] = next_level.id
        else:
            context['next_level'] = None

        if number_answered >= number_questions or level_passed:
            self.object.date_completed = timezone.now()
            self.object.state = HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE
            self.object.save()

        num_completed_levels = HarambeeJourneyModuleLevelRel.objects\
            .filter(harambee_journey_module_rel=self.object.harambee_journey_module_rel,
                    state=HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE)\
            .distinct('level')\
            .count()

        #CHECK IF MODULE COMPLETED
        if total_num_levels == num_completed_levels and \
                self.object.harambee_journey_module_rel != HarambeeJourneyModuleRel.MODULE_COMPLETED:

            context["last_level"] = True
            module_rel = HarambeeJourneyModuleRel.objects.get(id=self.object.harambee_journey_module_rel.id)
            module_rel.state = HarambeeJourneyModuleRel.MODULE_COMPLETED
            module_rel.date_completed = timezone.now()
            module_rel.save()
            harambee.send_sms('#HarambeeLearning. Congrats on completing your %s. Don\'t stop now! Register for '
                              'your next or redo the module to improve your score. Upskill for success.'
                              % module_rel.journey_module_rel.module.name)

            if has_completed_all_modules(harambee):
                harambee.send_sms('#HarambeeLearning. WOW you completed all the modules Harambee4work.mobi currently '
                                  'has online. More are on the way, we will let you know when they are loaded. Upskill'
                                  ' for success.')

        #CHECK IF MODULE HALF WAY COMPLETED
        elif num_completed_levels >= (total_num_levels / 2) and \
                self.object.harambee_journey_module_rel.state == HarambeeJourneyModuleRel.MODULE_STARTED:

            module_rel = HarambeeJourneyModuleRel.objects.get(id=self.object.harambee_journey_module_rel.id)
            module_rel.state = HarambeeJourneyModuleRel.MODULE_HALF
            module_rel.save()
            harambee.send_sms('#HarambeeLearning. Well done -  you are already halfway through your Harambee4work.mobi'
                              ' %s - don\'t stop now! Upskill for success.'
                              % module_rel.journey_module_rel.module.name)

        return context

    def get_object(self, queryset=None):
        harambee = Harambee.objects.get(id=self.request.session["user"]["id"])
        return HarambeeState.objects.get(harambee=harambee).active_level_rel


class QuestionView(DetailView):

    model = HarambeeJourneyModuleLevelRel
    template_name = "content/question.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestionView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        number_questions = self.object.level.get_num_questions()
        number_answers = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object).\
            aggregate(Count('id'))['id__count']

        level_passed = self.object.harambee_journey_module_rel.harambee.check_if_level_complete(self.object)
        if number_answers >= number_questions or level_passed:
            return HttpResponseRedirect("/level_end")
        return super(QuestionView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(QuestionView, self).get_context_data(**kwargs))

        question = self.object.current_question

        if not question or self.object.is_current_question_answered():
            question = harambee.get_next_question(self.object)
            self.object.current_question = question
            self.object.save()

        try:
            answer_time = HarambeeeQuestionAnswerTime.objects.get(harambee_level_rel=self.object, question=question)
            answer_time.start_time = timezone.now()
            answer_time.save()
        except HarambeeeQuestionAnswerTime.DoesNotExist:
            HarambeeeQuestionAnswerTime.objects.create(
                harambee=harambee,
                question=question,
                harambee_level_rel=self.get_object(),
                start_time=timezone.now()
            )

        context["question"] = question
        context["question_options"] = LevelQuestionOption.objects.filter(question__id=question.id).order_by('id')
        context["streak"] = harambee.answered_streak(self.object, False)
        if HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object)\
                .aggregate(Count('id'))['id__count'] == 0:
            context["message"] = "READY. SET. GO..."
        else:
            context["message"] = "YOUR NEXT QUESTION IS..."

        context["header_colour"] = "black-back"
        context["hide"] = False
        context["header_message"] = self.object.harambee_journey_module_rel.journey_module_rel.journey.name
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "answer" in request.POST.keys():
            answer_id = request.POST["answer"]

            options = self.object.current_question.levelquestionoption_set
            try:
                selected_option = options.get(pk=answer_id)
            except LevelQuestionOption.DoesNotExist:
                return HttpResponseRedirect("/question")

            harambee = Harambee.objects.get(id=kwargs.get("user")["id"])

            answered = harambee.answer_question(self.object.current_question, selected_option, self.object)
            #if false mean the question has been answered. Load next question
            if not answered:
                return HttpResponseRedirect("/question")

            answer_time = HarambeeeQuestionAnswerTime.objects.get(harambee_level_rel=self.object,
                                                                  question=self.object.current_question)
            answer_time.end_time = timezone.now()
            answer_time.save()

            if selected_option.correct:
                return HttpResponseRedirect("/right")
            else:
                return HttpResponseRedirect("/wrong")
        else:
            return HttpResponseRedirect("/question")

    def get_object(self, queryset=None):
        harambee = Harambee.objects.get(id=self.request.session["user"]["id"])
        state = get_harambee_state(harambee)
        return state.active_level_rel


class RightView(DetailView):

    model = HarambeeJourneyModuleLevelRel
    template_name = "content/right.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(RightView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        correct_message = ['GOOD WORK', 'NICELY DONE', 'IMPRESSIVE!', 'YOU ARE ON YOUR WAY', 'KEEP IT UP!',
                           'YOU ARE DOING GREAT', 'WELL DONE']
        context, harambee = get_harambee(self.request, super(RightView, self).get_context_data(**kwargs))
        context["question"] = self.object.current_question
        context["option"] = self.object.current_question.levelquestionoption_set.filter(correct=True).first()
        context["streak"] = harambee.answered_streak(self.object, True)
        if context["streak"] == 5:
            context["message"] = "5-in-a-Row! Well Done!"
        else:
            context["message"] = choice(correct_message)
        context["header_message"] = self.object.harambee_journey_module_rel.journey_module_rel.journey.name
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context

    def get_object(self, queryset=None):
        harambee = Harambee.objects.get(id=self.request.session["user"]["id"])
        return HarambeeState.objects.get(harambee=harambee).active_level_rel


class WrongView(DetailView):

    model = HarambeeJourneyModuleLevelRel
    template_name = "content/wrong.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(WrongView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        wrong_messages = ['KEEP TRYING', 'DON\'T GIVE UP', 'HAVE ANOTHER GO', 'NOPE. TRY AGAIN']
        context, harambee = get_harambee(self.request, super(WrongView, self).get_context_data(**kwargs))
        context["question"] = self.object.current_question
        context["option"] = self.object.current_question.levelquestionoption_set.filter(correct=True).first()
        context["streak"] = harambee.streak_before_ended(self.object)
        context["message"] = choice(wrong_messages)
        context["header_colour"] = "black-back"
        context["hide"] = False
        context["header_message"] = self.object.harambee_journey_module_rel.journey_module_rel.journey.name
        return context

    def get_object(self, queryset=None):
        harambee = Harambee.objects.get(id=self.request.session["user"]["id"])
        return HarambeeState.objects.get(harambee=harambee).active_level_rel


class HelpView(ListView):

    template_name = "misc/help.html"
    model = HelpPage

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HelpView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        pages = HelpPage.objects.filter(activate__lt=timezone.now()).filter(Q(deactivate__gt=timezone.now())
                                                                            | Q(deactivate=None))
        return pages

    def get_context_data(self, **kwargs):
        context, harambee = get_harambee(self.request, super(HelpView, self).get_context_data(**kwargs))
        user = self.request.session["user"]
        context["user"] = user
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context


class HelpPageView(DetailView):

    template_name = "misc/help_page.html"
    model = HelpPage

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HelpPageView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context, harambee = get_harambee(self.request, super(HelpPageView, self).get_context_data(**kwargs))
        user = self.request.session["user"]
        context["user"] = user
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context


class DeleteSMSView(TemplateView):

    template_name = 'admin/communication/delete_sms.html'

    @method_decorator(admin_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteSMSView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *arg, **kwargs):
        context = super(DeleteSMSView, self).get_context_data(*arg, **kwargs)
        sms_list = kwargs.get('ids')
        sms_list = map(int, sms_list.split(','))
        smses = Sms.objects.filter(id__in=sms_list)
        sent = smses.filter(sent=True)
        not_sent = smses.filter(sent=False)
        context['sent'] = sent
        context['not_sent'] = not_sent
        context['title'] = 'Are you sure?'
        return context

    def get(self, request, *args, **kwargs):
        sms_list = kwargs.get('ids')
        sms_list = map(int, sms_list.split(','))
        smses = Sms.objects.filter(id__in=sms_list)
        if smses:
            return super(DeleteSMSView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/admin/communication/sms/")

    def post(self, request, *args, **kwargs):
        if request.POST.get('post') == 'yes' and request.POST.get('action') == 'delete_selected':
            sms_list = request.POST.getlist('_selected_action')
            sms_list = [int(item) for item in sms_list]
            queryset = Sms.objects.filter(id__in=sms_list)
            count = queryset.aggregate(Count('id'))['id__count']
            queryset.delete()
            messages.add_message(request, messages.INFO, '%s SMSes deleted.' % count)
        return HttpResponseRedirect("/admin/communication/sms/")


class SendSMSView(TemplateView):
    template_name = 'admin/my_auth/send_sms.html'

    @method_decorator(admin_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SendSMSView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        harambee_id_list = kwargs.get('ids')
        harambee_id_list = map(int, harambee_id_list.split(','))
        harambee_queryset = Harambee.objects.filter(id__in=harambee_id_list)
        if harambee_queryset:
            return super(SendSMSView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/admin/my_auth/harambee/')

    def post(self, request, *args, **kwargs):
        if request.POST.get('post') == 'yes' and request.POST.get('action') == 'send_sms'\
                and request.POST.get('harambee') and request.POST.get('message'):
            harambee_list = request.POST.getlist('harambee')
            harambee_list = [int(item) for item in harambee_list]
            message = request.POST.get('message')

            queryset = Harambee.objects.filter(id__in=harambee_list)
            count = 0
            for harambee in queryset:
                count = count + 1 if harambee.send_sms(message) else count

            if count > 0:
                sms_text = '%d SMS created. It will be sent shortly.' % count if count == 1 \
                    else '%d SMSes created. They will be sent shortly.' % count
                messages.add_message(request, messages.INFO, sms_text)
            else:
                messages.add_message(request, messages.INFO, "No SMSes created.")
        return HttpResponseRedirect('/admin/my_auth/harambee/')

    def get_context_data(self, **kwargs):
        context = super(SendSMSView, self).get_context_data(**kwargs)
        harambee_id_list = kwargs.get('ids')
        harambee_id_list = map(int, harambee_id_list.split(','))
        harambee_queryset = Harambee.objects.filter(id__in=harambee_id_list)
        context['harambee_list'] = harambee_queryset
        context['title'] = 'Send SMS'
        return context