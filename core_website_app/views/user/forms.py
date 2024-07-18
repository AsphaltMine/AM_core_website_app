""" Form needed for the user part of everything
"""
from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core_website_app.components.account_request import (
    api as account_request_api,
)


class RequestAccountForm(UserCreationForm):
    """
    Form to request an account
    """

    username = forms.CharField(label="Username", max_length=100, required=True)
    firstname = forms.CharField(
        label="First Name", max_length=100, required=True
    )
    lastname = forms.CharField(
        label="Last Name", max_length=100, required=True
    )
    email = forms.EmailField(
        label="Email Address", max_length=100, required=True
    )
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password2"].help_text = ""

    class Meta:
        """Meta"""

        model = User
        fields = (
            "username",
            "firstname",
            "lastname",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Check email field

        Returns:

        """
        email = self.cleaned_data["email"]
        try:
            # Check if user with same email already exists
            account_request_api._get_user_by_email(email)
            # Raise validation error if found
            raise ValidationError("A user with that email already exists.")
        except ObjectDoesNotExist:
            return email


class ResendVerificationForm(forms.Form):
    """
    Form to resend the account verification email
    """

    email = forms.EmailField(
        label="Email Address", max_length=100, required=True
    )
    captcha = CaptchaField()


class ContactForm(forms.Form):
    """
    Form to contact the administrator
    """

    name = forms.CharField(label="Name", max_length=100, required=True)
    email = forms.EmailField(
        label="Email Address", max_length=100, required=True
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"class": "textarea_lock_h"}),
        required=True,
    )
    captcha = CaptchaField()
