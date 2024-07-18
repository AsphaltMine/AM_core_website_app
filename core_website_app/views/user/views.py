""" Views available for the user
"""
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from core_main_app.commons.exceptions import ApiError
from core_main_app.utils.markdown_parser import parse
from core_main_app.utils.rendering import render
import core_website_app.components.contact_message.api as contact_message_api
import core_website_app.components.help.api as help_api
import core_website_app.components.privacy_policy.api as privacy_policy_api
from core_website_app.components.rules_of_behavior import (
    api as rules_of_behavior_api,
)
import core_website_app.components.terms_of_use.api as terms_of_use_api

from core_website_app.components.contact_message.models import ContactMessage
from core_website_app.settings import DISPLAY_NIST_HEADERS
from .forms import RequestAccountForm, ContactForm, ResendVerificationForm


def _send_verification_email(request, user):
    """Email the user a link to verify their address and activate their account.

    Args:
        request:
        user:

    Returns:
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_url = request.build_absolute_uri(
        reverse(
            "core_website_app_verify_email",
            kwargs={"uidb64": uid, "token": token},
        )
    )
    context = {"user": user, "verification_url": verification_url}
    email = EmailMultiAlternatives(
        "Verify your AsphaltMine account",
        render_to_string(
            "core_website_app/user/email/verify_email.txt", context
        ),
        None,
        [user.email],
    )
    email.attach_alternative(
        render_to_string(
            "core_website_app/user/email/verify_email.html", context
        ),
        "text/html",
    )
    email.send()


def request_new_account(request):
    """Page that allows to request a user account

    Parameters:
        request:

    Returns: Http response
    """
    assets = {
        "js": [
            {
                "path": "core_website_app/user/js/user_account_req.js",
                "is_raw": False,
            }
        ],
        "css": ["core_main_app/user/css/login.css"],
    }

    if request.method == "POST":
        request_form = RequestAccountForm(request.POST)
        if request_form.is_valid():
            # Call the API
            try:
                request_form_data = request_form.cleaned_data

                user = User(
                    username=request_form_data.get("username"),
                    first_name=request_form_data.get("firstname"),
                    last_name=request_form_data.get("lastname"),
                    password=make_password(request_form_data.get("password1")),
                    email=request_form_data.get("email"),
                    is_active=False,
                )
                user.save()
                _send_verification_email(request, user)

                return render(
                    request,
                    "core_website_app/user/verify_email_sent.html",
                    assets=assets,
                    context={
                        "email": user.email,
                        "page_title": "Check Your Email",
                    },
                )
            except ApiError as exception:
                error_message = str(exception)

                error_template = get_template(
                    "core_website_app/user/request_error.html"
                )
                error_box = error_template.render(
                    {"error_message": error_message}
                )

                return render(
                    request,
                    "core_website_app/user/request_new_account.html",
                    assets=assets,
                    context={
                        "request_form": request_form,
                        "action_result": error_box,
                        "page_title": "Account Request",
                    },
                )
            except ValidationError as exception:
                error_message = (
                    "The following error(s) occurred during " "validation:"
                )
                error_items = [str(error) for error in exception.messages]

                error_template = get_template(
                    "core_website_app/user/request_error.html"
                )
                error_box = error_template.render(
                    {
                        "error_message": error_message,
                        "error_items": error_items,
                    }
                )

                return render(
                    request,
                    "core_website_app/user/request_new_account.html",
                    assets=assets,
                    context={
                        "request_form": request_form,
                        "action_result": error_box,
                        "page_title": "Account Request",
                    },
                )
    else:
        request_form = RequestAccountForm()

    return render(
        request,
        "core_website_app/user/request_new_account.html",
        assets=assets,
        context={
            "request_form": request_form,
            "page_title": "Account Request",
        },
    )


def verify_email(request, uidb64, token):
    """Activate the account if the verification link is valid.

    Parameters:
        request:
        uidb64:
        token:

    Returns: Http response
    """
    assets = {"css": ["core_main_app/user/css/login.css"]}
    try:
        user = User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(
        user, token
    ):
        if not user.is_active:
            user.is_active = True
            user.save()
        return render(
            request,
            "core_website_app/user/verify_email_result.html",
            assets=assets,
            context={"success": True, "page_title": "Email Verified"},
        )

    return render(
        request,
        "core_website_app/user/verify_email_result.html",
        assets=assets,
        context={"success": False, "page_title": "Verification Failed"},
    )


def resend_verification(request):
    """Page that allows a user to request a new verification email.

    Parameters:
        request:

    Returns: Http response
    """
    assets = {"css": ["core_main_app/user/css/login.css"]}
    if request.method == "POST":
        resend_form = ResendVerificationForm(request.POST)
        if resend_form.is_valid():
            email = resend_form.cleaned_data["email"]
            user = User.objects.filter(
                email__iexact=email, is_active=False
            ).first()
            if user is not None:
                _send_verification_email(request, user)

            return render(
                request,
                "core_website_app/user/verify_email_sent.html",
                assets=assets,
                context={
                    "email": email,
                    "page_title": "Check Your Email",
                },
            )
    else:
        resend_form = ResendVerificationForm()

    return render(
        request,
        "core_website_app/user/resend_verification.html",
        assets=assets,
        context={
            "resend_form": resend_form,
            "page_title": "Resend Verification Email",
        },
    )


def contact(request):
    """Contact form

    Parameters:
        request:

    Returns: Http response
    """

    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Call the API
            contact_message = ContactMessage(
                name=request.POST["name"],
                email=request.POST["email"],
                content=request.POST["message"],
            )

            contact_message_api.upsert(contact_message)
            messages.add_message(
                request,
                messages.INFO,
                "Your message has been sent to the administrator.",
            )
            return redirect(reverse("core_main_app_homepage"))
    else:
        contact_form = ContactForm()

    return render(
        request,
        "core_website_app/user/contact.html",
        context={"contact_form": contact_form, "page_title": "Contact"},
    )


def help_page(request):
    """Page that provides FAQ

    Parameters:
        request: Http response

    Returns:
    """
    # Call the API
    help_page_object = help_api.get()
    if help_page_object is not None:
        help_page_object.content = parse(help_page_object.content)

    return render(
        request,
        "core_website_app/user/help.html",
        context={"help": help_page_object, "page_title": "Help"},
        assets={"css": ["core_website_app/user/css/help.css"]},
    )


def privacy_policy(request):
    """Page that provides privacy policy

    Parameters:
        request:

    Returns: Http response
    """
    if DISPLAY_NIST_HEADERS:
        return HttpResponseRedirect("https://www.nist.gov/privacy-policy")

    # Call the API
    policy = privacy_policy_api.get()
    if policy is not None:
        policy.content = parse(policy.content)

    return render(
        request,
        "core_website_app/user/privacy-policy.html",
        context={"policy": policy, "page_title": "Privacy Policy"},
    )


def terms_of_use(request):
    """Page that provides terms of use

    Parameters:
        request:

    Returns: Http Response
    """
    # Call the API
    terms = terms_of_use_api.get()
    if terms is not None:
        terms.content = parse(terms.content)

    return render(
        request,
        "core_website_app/user/terms-of-use.html",
        context={"terms": terms, "page_title": "Terms of Use"},
    )


def rules_of_behavior(request):
    """Page that provides the rules of behavior

    Parameters:
        request:

    Returns: Http Response
    """
    # Call the API
    rules_of_behavior_object = rules_of_behavior_api.get()
    if rules_of_behavior_object is not None:
        rules_of_behavior_object.content = parse(
            rules_of_behavior_object.content
        )

    return render(
        request,
        "core_website_app/user/rules_of_behavior.html",
        context={
            "rules_of_behavior": rules_of_behavior_object,
            "page_title": "Rules of Behavior",
        },
    )
