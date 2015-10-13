from django.shortcuts import render
from utils import resolve_http_method
from core.models import Page
from my_auth.models import Harambee
from content.models import Journey, Module


NUMBER_OF_MODULES_PER_PAGE = 5


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


def journey_home(request, journey_id, page_count):

    journey = Journey.objects.get(id=journey_id)
    # TODO get recommended_module
    modules = journey.module_set.all()[:page_count*NUMBER_OF_MODULES_PER_PAGE]

    page = {'title': journey.name.upper()}

    page_count = int(page_count) + 1

    def get():
        return render(request, "content/journey_home.html", {"page": page, "modules": modules, "journey": journey,
                                                                  "page_count": page_count})

    def post():
        return render(request, "content/journey_home.html", {"page": page, "modules": modules, "journey": journey,
                                                                  "page_count": page_count})

    return resolve_http_method(request, [get, post])


def completed_modules(request, page_count):

    modules = Module.objects.filter()[:page_count*NUMBER_OF_MODULES_PER_PAGE]

    page = {'title': 'COMPLETED'}

    page_count = int(page_count) + 1

    def get():
        return render(request, "content/completed_modules.html", {"page": page, "modules": modules,
                                                                  "page_count": page_count})

    def post():
        return render(request, "content/completed_modules.html", {"page": page, "modules": modules,
                                                                  "page_count": page_count})

    return resolve_http_method(request, [get, post])


def module_intro(request, module_id):

    module = Module.objects.get(id=module_id)

    page = {'title': module.name.upper()}

    def get():
        return render(request, "content/module_intro.html", {"page": page, "module": module})

    def post():
        return render(request, "content/module_intro.html", {"page": page, "module": module})

    return resolve_http_method(request, [get, post])


def module_home(request, module_id):

    module = Module.objects.get(id=module_id)
    # TODO get levels
    levels = module.level_set.all()

    page = {'title': module.name.upper()}

    def get():
        return render(request, "content/module_home.html", {"page": page, "module": module, "levels": levels})

    def post():
        return render(request, "content/module_home.html", {"page": page, "module": module, "levels": levels})

    return resolve_http_method(request, [get, post])


