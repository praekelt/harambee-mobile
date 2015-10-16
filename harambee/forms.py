from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from my_auth.models import Harambee


class LoginForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")
    password = forms.CharField(
        label="PIN",
        widget=forms.PasswordInput
    )

    def is_valid(self):

        valid = super(LoginForm, self).is_valid()

        if not valid:
            return valid

        try:
            user = Harambee.objects.get(username=self.cleaned_data['username'])
        except Harambee.DoesNotExist:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['User does not exist'])
            return False

        if not self.cleaned_data['password'] == user.password:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Password is invalid'])
            return False

        return True


class JoinForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")
    password = forms.CharField(
        label="PIN",
        widget=forms.PasswordInput
    )


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
        if not existing_pin == user.password:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['Existing PIN incorrect'])
            return False

        if not self.cleaned_data['newPIN'] == self.cleaned_data['newPIN2']:
            self._errors[NON_FIELD_ERRORS] = self.error_class(['PINs do not match'])
            return False

        return True
