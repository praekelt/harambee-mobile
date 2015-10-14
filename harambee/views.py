from django.views.generic import View, DetailView, FormView, ListView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect, render
from core.models import Page, HelpPage
from my_auth.models import Harambee
from content.models import Journey, Module, Level, LevelQuestion
from harambee.forms import JoinForm, LoginForm, ResetPINForm, ChangePINForm, ChangeMobileNumberForm
from datetime import datetime


PAGINATE_BY = 5


def save_user_session(request, user):

    request.session["user"] = {}
    request.session["user"]["id"] = user.id
    request.session["user"]["name"] = user.first_name

    # update last login date
    user.last_login = datetime.now()
    user.save()


class PageView(DetailView):

    template_name = "misc/page.html"
    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)

        if self.kwargs.get('slug', None) == "welcome":
            self.template_name = "misc/welcome.html"

        if self.kwargs.get('slug', None) == "why_id":
            self.template_name = "misc/why_id.html"

        if self.kwargs.get('slug', None) == "intro":
            self.template_name = "misc/intro.html"
            context['user'] = self.request.session["user"]
            journeys = Journey.objects.filter(show_menu=True)
            context['journeys'] = journeys

        if self.kwargs.get('slug', None) == "no_match":
            self.template_name = "auth/no_match.html"

        if self.kwargs.get('slug', None) == "send_pin":
            self.template_name = "auth/send_pin.html"

        if self.kwargs.get('slug', None) == 'help':
            help_pages = HelpPage.objects.all()
            context['help_pages'] = help_pages

        return context


class HelpPageView(DetailView):

    template_name = "misc/help_page"
    model = HelpPage


class SearchView(View):

    template_name = "core/search.html"

    def get(self, request):
        return render(request, self.template_name)


class SearchResultView(ListView):

    model = Module
    template_name = "core/search_results.html"
    paginate_by = PAGINATE_BY

    def get(self, request):
        search_query = request.session["search_query"]

        context = {"search_query": search_query, "object_list": self.get_queryset()}

        return render(request, self.template_name, context)

    def post(self, request):
        search_query = "";
        if "search_query" in request.POST.keys():
            search_query = request.POST["search_query"]

        if search_query == "":
            if "current_search" in request.POST.keys():
                search_query = request.POST["current_search"]

        # TODO Update query set to search results
        self.queryset = Module.objects.all()

        self.request.session["search_query"] = search_query

        return HttpResponseRedirect("/search_results")


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

        # Check if user is registered
        exists = User.objects.filter(
            username=form.cleaned_data["username"]
        ).exists()

        if exists:
            if not user:
                user = Harambee.objects.get(username=form.cleaned_data["username"])
            self.request.session["user_exists"] = exists
            save_user_session(self.request, user)
            return super(LoginView, self).form_valid(form)


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


class ChangePinView(FormView):

    template_name = 'auth/change_pin.html'
    form_class = ChangePINForm
    success_url = '/successful_change_pin'

    def get_form_kwargs(self):

        kwargs = super(ChangePinView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):

        context = super(ChangePinView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="change_pin")
        context["page"] = page
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

    def get_context_data(self, **kwargs):

        context = super(ChangeMobileNumberView, self).get_context_data(**kwargs)
        page = Page.objects.get(slug="change_number")
        context["page"] = page
        return context

    def form_valid(self, form):

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        user.mobile = form.cleaned_data["mobile"]
        user.save()
        return super(ChangeMobileNumberView, self).form_valid(form)


class MenuView(View):
    template_name = "core/menu.html"

    def get(self, request):
        context = {}
        page = Page.objects.get(slug="menu")
        journeys = Journey.objects.filter(show_menu=True)
        user = self.request.session["user"]
        context['page'] = page
        context['journeys'] = journeys
        context['user'] = user
        return render(request, self.template_name, context)


class CompletedModuleView(ListView):

    model = Module
    template_name = "content/completed_modules.html"
    paginate_by = PAGINATE_BY
    queryset = Module.objects.all()  # TODO filter to show completed modules


class HomeView(ListView):

    model = Module
    template_name = "content/home.html"
    queryset = Module.objects.all()  # TODO filter to show active modules

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)
        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        context["user"] = user
        journeys = Journey.objects.filter(show_menu=True)
        context['journeys'] = journeys
        return context


class JourneyHomeView(ListView):

    template_name = "content/journey_home.html"
    paginate_by = PAGINATE_BY

    def get_context_data(self, **kwargs):

        context = super(JourneyHomeView, self).get_context_data(**kwargs)
        journey_slug = self.kwargs.get('slug', None)
        journey = Journey.objects.get(slug=journey_slug)
        context['journey'] = journey
        return context

    def get_queryset(self):
        journey_slug = self.kwargs.get('slug', None)
        journey = Journey.objects.get(slug=journey_slug)
        return journey.module_set.all()


class ModuleIntroView(DetailView):

    model = Module
    template_name = "content/module_intro.html"


class ModuleHomeView(ListView):

    template_name = "content/module_home.html"
    paginate_by = PAGINATE_BY

    def get_context_data(self, **kwargs):

        context = super(ModuleHomeView, self).get_context_data(**kwargs)
        module_slug = self.kwargs.get('slug', None)
        module = Module.objects.get(slug=module_slug)
        context['module'] = module
        return context

    def get_queryset(self):
        module_slug = self.kwargs.get('slug', None)
        module = Module.objects.get(slug=module_slug)
        return module.level_set.all()


class ModuleEndView(DetailView):

    model = Module
    template_name = "content/module_end.html"


class LevelIntroView(DetailView):

    model = Level
    template_name = "content/level_intro.html"


class LevelEndView(DetailView):

    model = Level
    template_name = "content/level_end.html"


class QuestionView(DetailView):

    model = LevelQuestion
    template_name = "content/question.html"


class RightView(DetailView):

    model = LevelQuestion
    template_name = "content/right.html"


class WrongView(DetailView):

    model = LevelQuestion
    template_name = "content/wrong.html"