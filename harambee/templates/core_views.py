from django.shortcuts import render

from content.models import Journey
from harambee.utils import resolve_http_method


def menu(request):
    #journeys = Journey.objects.filter(show_menu=True)
    journeys = [1]
    journeys[0] = {'name': 'Journey1', 'description': 'Description'}

    def get():
        return render(request, "content/home.html", {'journeys': journeys})

    def post():
        return render(request, "content/home.html")

    return resolve_http_method(request, [get, post])