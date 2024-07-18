""" Url router for the main application
"""
from django.conf.urls import include
from django.urls import re_path

from core_website_app.views.user import views as user_views

urlpatterns = [
    re_path("captcha/", include("captcha.urls")),
    re_path(
        r"^account-request/$",
        user_views.request_new_account,
        name="core_website_app_account_request",
    ),
    re_path(
        r"^verify-email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$",
        user_views.verify_email,
        name="core_website_app_verify_email",
    ),
    re_path(
        r"^resend-verification/$",
        user_views.resend_verification,
        name="core_website_app_resend_verification",
    ),
    re_path(
        r"^contact/$", user_views.contact, name="core_website_app_contact"
    ),
    re_path(r"^help/$", user_views.help_page, name="core_website_app_help"),
    re_path(
        r"^privacy/$",
        user_views.privacy_policy,
        name="core_website_app_privacy",
    ),
    re_path(
        r"^terms/$", user_views.terms_of_use, name="core_website_app_terms"
    ),
    re_path(
        r"^rules-of-behavior/$",
        user_views.rules_of_behavior,
        name="core_website_app_rules_of_behavior",
    ),
    re_path(r"^website/", include("core_website_app.rest.urls")),
]
