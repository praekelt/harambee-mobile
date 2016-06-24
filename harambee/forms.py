from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib.auth import authenticate
from my_auth.models import Harambee
from helper_functions import validate_credentials


class LoginForm(forms.Form):
    username = forms.CharField(label="ID NUMBER",  widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    password = forms.CharField(
        label="4 NUMERIC PIN",
        widget=forms.PasswordInput
    )

    def is_valid(self):
        if not validate_credentials(self, LoginForm):
            return False

        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if not user:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Incorrect ID/PIN.'])
            return False

        return True


class JoinForm(forms.Form):
    username = forms.CharField(label="ID NUMBER")
    password = forms.CharField(
        label="4 NUMERIC PIN",
        widget=forms.PasswordInput
    )

    def is_valid(self):
        return validate_credentials(self, JoinForm)


class ResetPINForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")

    def is_valid(self):

        valid = super(ResetPINForm, self).is_valid()
        if not valid:
            return valid

        try:
            Harambee.objects.get(username=self.cleaned_data['username'])
        except Harambee.DoesNotExist:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['User does not exist'])
            return False

        return True


class ChangeMobileNumberForm(forms.Form):
    mobile = forms.CharField(label="New mobile number")

    def is_valid(self):

        valid = super(ChangeMobileNumberForm, self).is_valid()
        if not valid:
            return valid

        mobile = str(self.cleaned_data['mobile'])

        if len(mobile) > 10:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Phone number to long'])
            return False
        elif len(mobile) < 10:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Phone number to short'])
            return False

        return True


class ChangePINForm(forms.Form):
    existingPIN = forms.CharField(label="Enter Existing PIN", widget=forms.PasswordInput)
    newPIN = forms.CharField(label="Enter New PIN", widget=forms.PasswordInput)
    newPIN2 = forms.CharField(label="Enter New PIN Again", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ChangePINForm, self).__init__(*args, **kwargs)

    def is_valid(self):

        valid = super(ChangePINForm, self).is_valid()
        if not valid:
            return valid

        user = Harambee.objects.get(id=self.request.session["user"]["id"])
        existing_pin = self.cleaned_data["existingPIN"]
        user = authenticate(username=user.username, password=existing_pin)
        if not user:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Existing PIN incorrect'])
            return False

        if not self.cleaned_data['newPIN'] == self.cleaned_data['newPIN2']:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['PINs do not match'])
            return False

        return True


class LevelIntroForm(forms.Form):
    level_id = forms.CharField(widget=forms.HiddenInput())


class ContactForm(forms.Form):
    first_name = forms.CharField(label='Name', max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'Name'}))
    last_name = forms.CharField(label='Surname', max_length=30, required=True,
                                widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'Surname'}))
    mobile = forms.DecimalField(label='Mobile', required=True,
                                widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'Mobile'}))
    id_number = forms.DecimalField(label='ID', required=True,
                                   widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'ID'}))
    message = forms.CharField(label='Message', required=True,
                              widget=forms.Textarea(attrs={'autocomplete': 'off',
                                                           'placeholder': 'Type your message...'}))
