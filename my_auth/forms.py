from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from my_auth.models import Harambee, SystemAdministrator


class SystemAdministratorCreationForm(forms.ModelForm):

    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = SystemAdministrator
        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(SystemAdministratorCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.mobile = user.username
        if commit:
            user.save()
        return user


class SystemAdministratorChangeForm(forms.ModelForm):

    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text="Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"password/\">this form</a>.")

    class Meta:
        model = SystemAdministrator
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class HarambeeCreationForm(forms.ModelForm):

    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    lps = forms.IntegerField(label='Learning Potential Score',
                             widget=forms.TextInput)
    mobile = forms.IntegerField(label='Mobile Number',
                                widget=forms.TextInput)
    username = forms.CharField(label='I.D. Number',
                               widget=forms.TextInput)
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = Harambee
        fields = '__all__'

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(HarambeeCreationForm, self).save(commit=False)
        user.mobile = self.cleaned_data["mobile"]
        user.lps = self.cleaned_data["lps"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class HarambeeChangeForm(forms.ModelForm):

    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text="Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"password/\">this form</a>.")

    def __init__(self, *args, **kwargs):
        super(HarambeeChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Harambee
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(HarambeeChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user