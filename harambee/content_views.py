from django.shortcuts import render
from utils import resolve_http_method
from core.models import Page
from my_auth.models import Harambee
from content.models import Journey


def home(request):

    try:
        #TODO retrieve user based on user.id
        user_model = Harambee.objects.get(id=0)
        if user_model:
            user = {'name': user_model.username}
    except Harambee.DoesNotExist:
        user = {'name': 'Herman'}

    #journeys = Journey.objects.filter(show_menu=True)
    journeys = [1]
    journeys[0] = {'name': 'Journey1', 'description': 'Description'}

    #TODO get active modules
    active_modules = [1]
    active_modules[0] = {'name': 'Module', 'progress': 'Progress'}

    def get():
        return render(request, "content/home.html", {"user": user, "active_modules": active_modules, 'journeys': journeys})

    def post():
        return render(request, "content/home.html")

    return resolve_http_method(request, [get, post])


def journey_home(request, journey_id, page):

    NUMBER_OF_MODULES_PER_PAGE = 5

    journey = Journey.objects.get(id=journey_id)
    modules = journey.module_set.all()[:page*NUMBER_OF_MODULES_PER_PAGE]


