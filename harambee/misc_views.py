from django.shortcuts import render
from utils import resolve_http_method
from core.models import Page
from my_auth.models import Harambee
from content.models import Journey


def welcome(request):

    try:
        page_model = Page.objects.get(lookup="welcome")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'WELCOME', 'heading': 'Welcome',
                'content': 'Are you 18 - 28 years old, with a matric degree/diploma and struggling to find a job? '
                           'Harmabee can help. Go on a journey of career discovery and learn what it takes to get the '
                           'job that is right for you!'}

    def get():
        return render(request, "misc/welcome.html", {"page": page})

    def post():
        return render(request, "misc/welcome.html")

    return resolve_http_method(request, [get, post])


def why_id(request):

    try:
        page_model = Page.objects.get(lookup="why_id")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'WHY DO YOU NEED MY I.D. NUMBER?', 'heading': 'Why do we need your I.D. number?',
                'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ullamcorper, nisl congue '
                           'pulvinar faucibus, nibh justo eleifend orci, eget mattis augue lacus eu sem. Nullam tempus'
                           ' rutrum velit ac suscipit. Pellentesque nec lacus sit amet erat vestibulum laoreet '
                           'ultricies non augue.Suspendisse vehicula massa et augue lobortis vehicula.'}

    def get():
        return render(request, "misc/page.html", {"page": page})

    def post():
        return render(request, "misc/page.html")

    return resolve_http_method(request, [get, post])


def terms(request):

    try:
        page_model = Page.objects.get(lookup="terms")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'TERMS AND CONDITIONS', 'heading': 'Terms and Conditions',
                'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ullamcorper, nisl congue '
                           'pulvinar faucibus, nibh justo eleifend orci, eget mattis augue lacus eu sem. Nullam tempus'
                           ' rutrum velit ac suscipit. Pellentesque nec lacus sit amet erat vestibulum laoreet '
                           'ultricies non augue.Suspendisse vehicula massa et augue lobortis vehicula.'}

    def get():
        return render(request, "misc/page.html", {"page": page})

    def post():
        return render(request, "misc/page.html")

    return resolve_http_method(request, [get, post])


def about(request):

    try:
        page_model = Page.objects.get(lookup="about")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'ABOUT', 'heading': 'About',
                'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ullamcorper, nisl congue '
                           'pulvinar faucibus, nibh justo eleifend orci, eget mattis augue lacus eu sem. Nullam tempus'
                           ' rutrum velit ac suscipit. Pellentesque nec lacus sit amet erat vestibulum laoreet '
                           'ultricies non augue.Suspendisse vehicula massa et augue lobortis vehicula.'}

    def get():
        return render(request, "misc/page.html", {"page": page})

    def post():
        return render(request, "misc/page.html")

    return resolve_http_method(request, [get, post])


def contact(request):

    try:
        page_model = Page.objects.get(lookup="contact")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'CONTACT US', 'heading': 'Contact Us',
                'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ullamcorper, nisl congue '
                           'pulvinar faucibus, nibh justo eleifend orci, eget mattis augue lacus eu sem. Nullam tempus'
                           ' rutrum velit ac suscipit. Pellentesque nec lacus sit amet erat vestibulum laoreet '
                           'ultricies non augue.Suspendisse vehicula massa et augue lobortis vehicula.'}

    def get():
        return render(request, "misc/page.html", {"page": page})

    def post():
        return render(request, "misc/page.html")

    return resolve_http_method(request, [get, post])


def intro(request):

    try:
        page_model = Page.objects.get(lookup="intro")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'INTRODUCTION', 'heading': 'Introduction',
                'content': "Get started by choosing which journey you'd like to explore..."}

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

    def get():
        return render(request, "misc/intro.html", {"user": user, "page": page, 'journeys': journeys})

    def post():
        return render(request, "misc/intro.html")

    return resolve_http_method(request, [get, post])
