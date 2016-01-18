from __future__ import division
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, FormView, ListView, TemplateView
from django.contrib.auth import logout
from my_auth.models import HarambeeLog
from django.shortcuts import HttpResponseRedirect, redirect, render
from core.models import Page, HelpPage
from content.models import Journey, Module, Level, HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, \
    JourneyModuleRel, HarambeeState, LevelQuestionOption, HarambeeQuestionAnswer, HarambeeeQuestionAnswerTime
from harambee.forms import *
from haystack.views import SearchView
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from functools import wraps
from helper_functions import get_live_journeys, get_menu_journeys, get_recommended_modules,\
    get_harambee_completed_modules, get_module_data_by_journey, get_harambee_active_levels,\
    get_harambee_locked_levels, get_level_data, get_all_module_data, get_module_data, get_module_data_from_queryset,\
    unlock_first_level, validate_id
from rolefit.communication import *
from random import randint
from django.db.models import Q
import httplib2
from communication.tasks import send_single_sms

PAGINATE_BY = 5


def save_user_session(request, user):

    request.session["user"] = {}
    request.session["user"]["id"] = user.id
    request.session["user"]["name"] = user.first_name

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

        valid = validate_id(username)
        if not valid:
            form.add_error('username', "ID number is incorrect. An ID number is 13 digits only. Please try again.")
            return super(JoinView, self).form_invalid(form)

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

            # check if there is a user with retrieved candidate_id
            try:
                Harambee.objects.get(candidate_id=harambee['candidateId'])
                # TODO: add email address
                return render(self.request, 'misc/error.html',
                              {'title': 'REGISTRATION ERROR', 'header': 'Registration Error',
                               'message': 'An error occurred with your registration. Please contact the admin to '
                                          'assist you. <a href="mailto:" style="color: #0000FF;">Email Harambee.</a>'},
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

                save_user_session(self.request, user)
                get_harambee_state(user)
                return HttpResponseRedirect("/intro")


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = '/home'

    def get_context_data(self, **kwargs):

        context = super(LoginView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="login")
        context["page"] = page
        context["header_colour"] = "green-back"
        context["hide"] = True
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(username=form.cleaned_data["username"])

        if not user.last_login:
            save_user_session(self.request, user)
            get_harambee_state(user)
            return HttpResponseRedirect("/intro")

        save_user_session(self.request, user)
        HarambeeLog.objects.create(harambee=user, date=datetime.now(), action=HarambeeLog.LOGIN)
        return super(LoginView, self).form_valid(form)


class LogoutView(View):

    def get(self, request, **kwargs):
        user = self.request.session["user"]
        harambee = Harambee.objects.get(id=user['id'])
        logout(request)
        HarambeeLog.objects.create(harambee=harambee, date=datetime.now(), action=HarambeeLog.LOGOUT)
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

        user = Harambee.objects.get(username=form.cleaned_data["username"])

        new_pin = self.generate_random_pin()
        user.set_password(new_pin)
        user.save()

        message = 'Your new Harambee 4 digit PIN is: %s.' % new_pin

        send_single_sms.delay(user, message)

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

    model = Module
    template_name = "content/home.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(HomeView, self).get_context_data(**kwargs))
        user = self.request.session["user"]
        context["user"] = user
        context['journeys'] = get_live_journeys()
        context['header_message'] = "Hello %s" % user["name"]
        context["module_list"] = get_all_module_data(harambee)
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
        context["recommended_modules"] = get_recommended_modules(journey, harambee)
        context["module_list"] = get_module_data_by_journey(harambee, journey)
        context["header_colour"] = "black-back"
        context["hide"] = False
        return context


#TODO: check if the right view class is used
class ModuleIntroView(TemplateView):

    template_name = "content/module_intro.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleIntroView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(ModuleIntroView, self).get_context_data(**kwargs))
        module_slug = self.kwargs.get('module_slug', None)
        journey_slug = self.kwargs.get('journey_slug', None)
        journey_module_rel = JourneyModuleRel.objects.get(journey__slug=journey_slug, module__slug=module_slug)
        context["object"] = journey_module_rel
        context["user"] = harambee
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
        journey_module_rel = JourneyModuleRel.objects.get(journey__slug=journey_slug, module__slug=module_slug)
        harambee = Harambee.objects.get(id=user['id'])
        try:
            rel = HarambeeJourneyModuleRel.objects.get(journey_module_rel=journey_module_rel, harambee=harambee)
            try:
                HarambeeJourneyModuleLevelRel.objects.get(harambee_journey_module_rel=rel)
            except HarambeeJourneyModuleLevelRel.DoesNotExist:
                unlock_first_level(rel)
            except HarambeeJourneyModuleLevelRel.MultipleObjectsReturned:
                pass
            return super(ModuleHomeView, self).get(self, request, *args, **kwargs)
        except HarambeeJourneyModuleRel.DoesNotExist:
            rel = HarambeeJourneyModuleRel.objects.create(
                journey_module_rel=journey_module_rel,
                harambee=harambee,
                date_started=datetime.now())
            unlock_first_level(rel)
            return HttpResponseRedirect("/module_intro/%s/%s" % (journey_module_rel.journey.slug,
                                                                 journey_module_rel.module.slug))

    def get_context_data(self, **kwargs):
        context, harambee = get_harambee(self.request, super(ModuleHomeView, self).get_context_data(**kwargs))

        # TODO: Maybe move this to a method with exceptions and redirect if it fails to find the object
        module_slug = self.kwargs.get('module_slug', None)
        journey_slug = self.kwargs.get('journey_slug', None)
        journey_module_rel = JourneyModuleRel.objects.get(journey__slug=journey_slug, module__slug=module_slug)

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
        return JourneyModuleRel.objects.get(journey__slug=journey_slug, module__slug=module_slug)


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
        journey_module_rel = JourneyModuleRel.objects.get(journey__slug=journey_slug, module__slug=module_slug)
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

        context = super(LevelEndView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        context["message"] = "WELL DONE"
        context["header_colour"] = "black-back"
        context["hide"] = False

        number_questions = self.object.level.get_num_questions()
        number_answered = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object,).\
            aggregate(Count('id'))['id__count']
        number_correct = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=self.object,
                                                               option_selected__correct=True).\
            aggregate(Count('id'))['id__count']

        number_levels = self.object.harambee_journey_module_rel.journey_module_rel.module.level_set.all()\
            .aggregate(Count('id'))['id__count']
        level_order = self.object.level.order

        correct_percentage = 0
        if number_questions != 0:
            correct_percentage = round(number_correct * 100 / number_questions, 1)

        incorrect_percentage = round(100 - correct_percentage, 1)

        if number_answered >= number_questions:
            self.object.date_completed = datetime.now()
            self.object.state = HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE
            self.object.save()

        context["correct"] = correct_percentage
        context["incorrect"] = incorrect_percentage

        context["header_message"] = self.object.harambee_journey_module_rel.journey_module_rel.journey.name

        if number_levels == level_order:
            context["last_level"] = True
            HarambeeJourneyModuleRel.objects.filter(id=self.object.harambee_journey_module_rel.id)\
                .update(state=HarambeeJourneyModuleRel.MODULE_COMPLETE)
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
        if number_answers >= number_questions:
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
            answer_time.start_time = datetime.now()
            answer_time.save()
        except HarambeeeQuestionAnswerTime.DoesNotExist:
            HarambeeeQuestionAnswerTime.objects.create(
                harambee=harambee,
                question=question,
                harambee_level_rel=self.get_object(),
                start_time=datetime.now()
            )

        context["question"] = question
        context["streak"] = harambee.answered_streak(self.object, False)
        context["message"] = "You are doing great"
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

            harambee.answer_question(self.object.current_question, selected_option, self.object)
            harambee.check_if_level_complete(self.object)

            answer_time = HarambeeeQuestionAnswerTime.objects.get(harambee_level_rel=self.object,
                                                                  question=self.object.current_question)
            answer_time.end_time = datetime.now()
            answer_time.save()

            if selected_option.correct:
                return HttpResponseRedirect("/right")
            else:
                return HttpResponseRedirect("/wrong")
        else:
            return HttpResponseRedirect("/question")

    def get_object(self, queryset=None):
        harambee = Harambee.objects.get(id=self.request.session["user"]["id"])
        return HarambeeState.objects.get(harambee=harambee).active_level_rel


class RightView(DetailView):

    model = HarambeeJourneyModuleLevelRel
    template_name = "content/right.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(RightView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(RightView, self).get_context_data(**kwargs))
        context["question"] = self.object.current_question
        context["option"] = self.object.current_question.levelquestionoption_set.filter(correct=True).first()
        context["streak"] = harambee.answered_streak(self.object, True)
        if context["streak"] == 5:
            context["message"] = "Well Done!"
        else:
            context["message"] = "You are half way there"
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

        context, harambee = get_harambee(self.request, super(WrongView, self).get_context_data(**kwargs))
        context["question"] = self.object.current_question
        context["option"] = self.object.current_question.levelquestionoption_set.filter(correct=True).first()
        context["streak"] = harambee.streak_before_ended(self.object)
        context["message"] = "You are getting there"
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
        pages = HelpPage.objects.filter(activate__lt=datetime.now()).filter(Q(deactivate__gt=datetime.now())
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
