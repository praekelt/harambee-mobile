from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")
    password = forms.CharField(
        label="PIN",
        widget=forms.PasswordInput
    )


class ResetPINForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")