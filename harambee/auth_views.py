from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from lockout import LockedOut

from core.models import Page
from my_auth.models import Harambee
from harambee.forms import LoginForm, ResetPINForm
from harambee.utils import resolve_http_method


def join(request):

    try:
        page_model = Page.objects.get(lookup="join")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading}
    except Page.DoesNotExist:
        page = {'title': 'JOIN', 'heading': 'JOIN'}

    def get():
        return render(request, "auth/join.html", {"page": page})

    def post():
        return render(request, "auth/join.html", {"page": page})

    return resolve_http_method(request, [get, post])


def login(request):

    try:
        page_model = Page.objects.get(lookup="login")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading}
    except Page.DoesNotExist:
        page = {'title': 'LOG IN', 'heading': 'LOG IN'}

    def get():
        return render(request, "auth/login.html", {"page": page,
                                                   "form": LoginForm()})

    def post():
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                # Check if this is a registered user
                user = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"]
                )
            except LockedOut:
                request.session["user_lockout"] = True
                return redirect("auth.no_match")

            # Check if user is registered
            exists = User.objects.filter(
                username=form.cleaned_data["username"]
            ).exists()
            request.session["user_exists"] = exists
            return redirect("misc.intro")
        else:
            return get()

    return resolve_http_method(request, [get, post])


def forgot_pin(request):

    try:
        page_model = Page.objects.get(lookup="forgot_pin")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'FORGOT PIN', 'heading': 'No Problem.',
                'content': "Just give us your I.D. number and we'll send an SMS to the number we have on file for you "
                           "with your new PIN."}

    def get():
        return render(request, "auth/forgot_pin.html", {"page": page, "form": ResetPINForm()})

    def post():
        form = ResetPINForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            print "Hello %s" % username
            return send_pin(request)
        return render(request, "auth/forgot_pin.html", {"page": page})

    return resolve_http_method(request, [get, post])


def send_pin(request):

    try:
        page_model = Page.objects.get(lookup="send_pin")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'SEND PIN CONFORMATION', 'heading': 'Done.',
                'content': "Your new PIN will be sent to you by SMS shortly. Use the new PIN with your usual I.D. "
                           "number to login."}

    def get():
        return render(request, "auth/send_pin.html", {"page": page})

    def post():
        return render(request, "auth/send_pin.html", {"page": page})

    return resolve_http_method(request, [get, post])


def no_match(request):

    try:
        page_model = Page.objects.get(lookup="no_match")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading, 'content': page_model.content}
    except Page.DoesNotExist:
        page = {'title': 'NO MATCH', 'heading': 'No match.',
                'content': "Sorry your I.D. number does not match any Harambees we have on record. Right now, only "
                           "those that have attended training at Harambee can join this platform."}

    def get():
        return render(request, "auth/no_match.html", {"page": page})

    def post():
        return render(request, "auth/no_match.html", {"page": page})

    return resolve_http_method(request, [get, post])


def profile(request):

    #TODO get user by id
    user = Harambee.objects.get(id=0)

    def get():
        return render(request, "auth/profile.html", {"user": user})

    def post():
        return render(request, "auth/profile.html", {"user": user})

    return resolve_http_method(request, [get, post])