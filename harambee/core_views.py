from django.shortcuts import render

from content.models import Journey, Module
from harambee.utils import resolve_http_method


def menu(request):
    #journeys = Journey.objects.filter(show_menu=True)
    journeys = [1]
    journeys[0] = {'name': 'Journey1', 'description': 'Description'}

    def get():
        return render(request, "core/menu.html", {'journeys': journeys})

    def post():
        return render(request, "core/menu.html")

    return resolve_http_method(request, [get, post])


def search(request):

    def get():
        return render(request, "core/search.html")

    def post():
        return render(request, "core/search.html")

    return resolve_http_method(request, [get, post])


def search_results(request):

    def get():
        return render(request, "core/search.html")

    def post():

        page_count = 1;
        if "page_count" in request.POST.keys():
            page_count = request.POST["page_count"]

        search_query = "";
        if "search_query" in request.POST.keys():
            search_query = request.POST["search_query"]

        if search_query == "":
            if "current_search" in request.POST.keys():
                search_query = request.POST["current_search"]

        #TODO search for modules
        modules = Module.objects.filter(id=0)

        return render(request, "core/search_results.html", {"search_query": search_query, "page_count": page_count,
                                                            "modules": modules})

    return resolve_http_method(request, [get, post])

