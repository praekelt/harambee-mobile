from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")
    password = forms.CharField(
        label="PIN",
        widget=forms.PasswordInput
    )


class ResetPINForm(forms.Form):
    username = forms.CharField(label="I.D. NUMBER")


class ChangeMobileNumberForm(forms.Form):
    mobile = forms.CharField(label="New mobile number")


class ChangePINForm(forms.Form):
    existingPIN = forms.CharField(label="Enter Existing PIN")
    newPIN = forms.CharField(label="Enter New PIN")
    newPIN2 = forms.CharField(label="Enter New PIN Again")
