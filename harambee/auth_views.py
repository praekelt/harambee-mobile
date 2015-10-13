from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from lockout import LockedOut

from core.models import Page
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


def login(request, state):

    try:
        page_model = Page.objects.get(lookup="login")
        if page_model:
            page = {'title': page_model.title, 'heading': page_model.heading}
    except Page.DoesNotExist:
        page = {'title': 'LOG IN', 'heading': 'LOG IN'}

    def get():
        return render(request, "auth/login.html", {"page": page, "state": state,
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

            if user is not None and user.is_active:
                try:
                    registered = is_registered(user)
                    class_active = is_class_active(user)
                    if registered is not None and class_active:
                        save_user_session(request, registered, user)

                        usr = Learner.objects.filter(username=form.cleaned_data["username"])
                        par = Participant.objects.filter(learner=usr, is_active=True)

                        if len(par) > 1:
                            subject = ' '.join([
                                'Multiple participants active -',
                                usr.first().first_name,
                                usr.first().last_name,
                                '-',
                                usr.first().username
                            ])
                            message = '\n'.join([
                                'Student: ' + usr.first().first_name + ' ' + usr.first().last_name,
                                'Msisdn: ' + usr.first().username,
                                'is unable to login due to having multiple active participants.',
                                'To fix this, some participants  will have to be deactivated.'
                            ])

                            mail_managers(
                                subject=subject,
                                message=message,
                                fail_silently=False
                            )
                            return render(request, "misc/account_problem.html")

                        event = Event.objects.filter(course=par.first().classs.course,
                                                     activation_date__lte=datetime.now(),
                                                     deactivation_date__gt=datetime.now()
                                                     ).first()

                        if event:
                            allowed, event_participant_rel = par.first().can_take_event(event)
                            if allowed:
                                return redirect("learn.event_splash_page")

                        if ParticipantQuestionAnswer.objects.filter(participant=par).count() == 0:
                            return redirect("learn.first_time")
                        else:
                            return redirect("learn.home")
                    else:
                        return redirect("auth.getconnected")
                except ObjectDoesNotExist:
                    request.session["wrong_password"] = False
                    return redirect("auth.getconnected")
            else:
                # Save provided username
                request.session["user_lockout"] = False
                request.session["username"] = form.cleaned_data["username"]
                request.session["wrong_password"] = True
                return redirect("auth.getconnected")
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