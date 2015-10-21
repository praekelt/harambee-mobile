from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from haystack.views import SearchView
from django.views.generic import DetailView, FormView, ListView, View
from django.contrib.auth import authenticate
from django.shortcuts import HttpResponseRedirect, redirect
from core.models import Page, HelpPage
from my_auth.models import Harambee
from content.models import Journey, Module, Level, LevelQuestion, HarambeeLevelRel, HarambeeQuestionAnswer, COMPLETE, \
    HarambeeModuleRel, LevelQuestionOption
from harambee.forms import JoinForm, LoginForm, ResetPINForm, ChangePINForm, ChangeMobileNumberForm, LevelIntroForm
from django.utils import timezone
from functools import wraps
from django.db.models import Count


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


class PageView(DetailView):

    template_name = "misc/page.html"
    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)

        if self.kwargs.get('slug', None) == "welcome":
            self.template_name = "misc/welcome.html"

        if self.kwargs.get('slug', None) == "why_id":
            self.template_name = "misc/why_id.html"

        if self.kwargs.get('slug', None) == "no_match":
            self.template_name = "auth/no_match.html"

        if self.kwargs.get('slug', None) == "send_pin":
            self.template_name = "auth/send_pin.html"

        return context


class HelpView(ListView):

    template_name = "misc/help.html"
    model = HelpPage

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HelpView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="help")
        context["page"] = page
        return context


class HelpPageView(DetailView):

    template_name = "misc/help_page"
    model = HelpPage

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HelpPageView, self).dispatch(*args, **kwargs)


class CustomSearchView(SearchView):

    def extra_context(self):
        extra = super(CustomSearchView, self).extra_context()

        rels = {}
        user_id = self.request.session["user"]["id"]
        if not self.results == []:
            for result in self.results:
                user_rels = HarambeeModuleRel.objects.filter(harambee__id=user_id, module__id=result.id).first()
                rels[result.id] = user_rels

        extra["rels"] = rels

        return extra


class JoinView(FormView):

    template_name = 'auth/join.html'
    form_class = JoinForm
    success_url = '/home'

    def get_context_data(self, **kwargs):

        context = super(JoinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="join")
        context["page"] = page
        return context

    def form_valid(self, form):
        exists = False  # TODO Check against Harambee SQL
        if not exists:
            return HttpResponseRedirect('/no_match')
        #TODO create user in our db
        #TODO login
        return super(JoinView, self).form_valid(form)


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = '/home'

    def get_context_data(self, **kwargs):

        context = super(LoginView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="login")
        context["page"] = page
        return context

    def form_valid(self, form):

        # Check if this is a registered user
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"]
        )

        if not user:
            user = Harambee.objects.get(username=form.cleaned_data["username"])
        if not user.last_login:
            save_user_session(self.request, user)
            return HttpResponseRedirect("/intro")
        save_user_session(self.request, user)
        return super(LoginView, self).form_valid(form)


class LogoutView(View):

    def get(self, request):
        logout(request)

        return HttpResponseRedirect("/")


class ForgotPinView(FormView):
    template_name = 'auth/forgot_pin.html'
    form_class = ResetPINForm
    success_url = '/send_pin'

    def get_context_data(self, **kwargs):

        context = super(ForgotPinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="forgot_pin")
        context["page"] = page
        return context

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        user = Harambee.objects.get(username=username)
        # TODO send new pin
        user.password = "0000"
        user.save()
        return super(ForgotPinView, self).form_valid(form)


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
        return context


class ChangePinView(FormView):

    template_name = 'auth/change_pin.html'
    form_class = ChangePINForm
    success_url = '/successful_change_pin'

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
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        user.password = form.cleaned_data["newPIN"]
        user.save()
        return super(ChangePinView, self).form_valid(form)


class ChangeMobileNumberView(FormView):

    template_name = 'auth/change_number.html'
    form_class = ChangeMobileNumberForm
    success_url = '/successful_change_number'

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChangeMobileNumberView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ChangeMobileNumberView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="change_number")
        user = self.request.session["user"]
        context["page"] = page
        context["user"] = user
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        user.mobile = form.cleaned_data["mobile"]
        user.save()
        return super(ChangeMobileNumberView, self).form_valid(form)


class IntroView(ListView):

    template_name = "misc/intro.html"
    model = Journey
    query_set = Journey.objects.filter(show_menu=True)

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(IntroView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(IntroView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class MenuView(DetailView):
    model = Page
    template_name = "core/menu.html"

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
        return context


class CompletedModuleView(ListView):

    model = Module
    template_name = "content/completed_modules.html"
    paginate_by = PAGINATE_BY
    queryset = Module.objects.all()  # TODO filter to show completed modules

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(CompletedModuleView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(CompletedModuleView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class HomeView(ListView):

    model = Module
    template_name = "content/home.html"
    queryset = Module.objects.all()  # TODO filter to show active modules

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        journeys = Journey.objects.filter(show_menu=True)
        context['journeys'] = journeys
        return context


class JourneyHomeView(ListView):

    template_name = "content/journey_home.html"
    paginate_by = PAGINATE_BY

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(JourneyHomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(JourneyHomeView, self).get_context_data(**kwargs)
        journey_slug = self.kwargs.get('slug', None)
        journey = Journey.objects.get(slug=journey_slug)
        user = self.request.session["user"]
        context['journey'] = journey
        context["user"] = user
        return context

    def get_queryset(self):
        journey_slug = self.kwargs.get('slug', None)
        journey = Journey.objects.get(slug=journey_slug)
        return journey.module_set.all()


class ModuleIntroView(DetailView):

    model = Module
    template_name = "content/module_intro.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleIntroView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ModuleIntroView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class ModuleHomeView(ListView):

    template_name = "content/module_home.html"
    paginate_by = PAGINATE_BY

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleHomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ModuleHomeView, self).get_context_data(**kwargs)
        module_slug = self.kwargs.get('slug', None)
        module = Module.objects.get(slug=module_slug)
        user = self.request.session["user"]
        context['module'] = module
        context["user"] = user
        return context

    def get_queryset(self):
        module_slug = self.kwargs.get('slug', None)
        module = Module.objects.get(slug=module_slug)
        return module.level_set.all()


class ModuleEndView(DetailView):

    model = Module
    template_name = "content/module_end.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModuleEndView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ModuleEndView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class LevelIntroView(DetailView):

    model = Level
    form_class = LevelIntroForm
    template_name = "content/level_intro.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(LevelIntroView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        if form.is_valid():
            user = self.request.session["user"]
            harambee = Harambee.objects.get(id=user["id"])

            level_id = form.cleaned_data["level_id"]

            try:
                level = Level.objects.get(id=level_id)
            except Level.DoesNotExist:
                return HttpResponseRedirect("/home")

            if not HarambeeLevelRel.objects.filter(harambee=harambee, level=level).exists():
                rel = HarambeeLevelRel.objects.create(harambee=harambee, level=level, attempt=1)
            else:
                if HarambeeLevelRel.objects.filter(harambee=harambee, level=level).exclude(state=COMPLETE).exists():
                    rel = HarambeeLevelRel.objects.filter(harambee=harambee, level=level)\
                        .exclude(state=COMPLETE).first()
                else:
                    count = HarambeeLevelRel.objects.filter(harambee=harambee, level=level, state=COMPLETE)\
                        .aggregate(Count('id'))['id__count'] + 1
                    rel = HarambeeLevelRel.objects.create(harambee=harambee, level=level, attempt=count)

            return HttpResponseRedirect("/question/%s" % rel.id)


class LevelEndView(DetailView):

    model = Level
    template_name = "content/level_end.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(LevelEndView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(LevelEndView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class QuestionView(DetailView):

    model = HarambeeLevelRel
    template_name = "content/question.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestionView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context, harambee = get_harambee(self.request, super(QuestionView, self).get_context_data(**kwargs))

        next_question = harambee.get_next_question(self.object)
        if not next_question:
            return HttpResponseRedirect("/")

        context["question"] = next_question

        return context

    def post(self, request, *args, **kwargs):
        if request._post.has_key("answer") and request._post.has_key("question") and request._post.has_key(""):

            try:
                question = LevelQuestion.objects.get(pk=request._post.key("question"))
            except LevelQuestion.DoesNotExist:
                return

            options = question.levelquestionoption_set

            try:
                answer = options.get(pk=request._post.key("answer"))
            except HarambeeQuestionAnswer.DoesNotExist:
                return

            context, harambee = get_harambee(self.request, super(QuestionView, self).get_context_data(**kwargs))

            harambee.answer_question(answer.question, answer)

            if answer.correct:
                pass
            else:
                pass

        return HttpResponseRedirect('')


class RightView(DetailView):

    model = LevelQuestion
    template_name = "content/right.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(RightView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(RightView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context


class WrongView(DetailView):

    model = LevelQuestion
    template_name = "content/wrong.html"

    @method_decorator(harambee_login_required)
    def dispatch(self, *args, **kwargs):
        return super(WrongView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(WrongView, self).get_context_data(**kwargs)
        user = self.request.session["user"]
        context["user"] = user
        return context