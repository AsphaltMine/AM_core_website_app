""" Account request API
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import core_main_app.utils.notifications.mail as send_mail_api
from core_main_app.commons.exceptions import ApiError
from core_website_app.components.account_request.models import AccountRequest
from core_website_app.settings import (
    SERVER_URI,
    EMAIL_DENY_SUBJECT,
)


def get_all():
    """List of opened account requests"""
    return AccountRequest.get_all()


def get_count():
    """Count number of account request currently in the database"""
    return get_all().count()


def get(account_request_id):
    """Get an account request given its primary key"""
    try:
        return AccountRequest.get_by_id(account_request_id)
    except Exception:
        raise ApiError("No request could be found with the given id.")


def insert(user):
    """Create a new request"""
    try:
        _get_user_by_username(user.username)
        raise ApiError("A user with the same username already exists.")
    except ObjectDoesNotExist:
        pass

    try:
        _get_user_by_email(user.email)
        raise ApiError("A user with the same email already exists.")
    except ObjectDoesNotExist:
        pass

    user.save()

    account_request = AccountRequest(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )

    context = {"URI": SERVER_URI}
    template_path = (
        "core_website_app/admin/email/request_account_for_admin.html"
    )
    send_mail_api.send_mail_to_administrators(
        subject="New Account Request",
        path_to_template=template_path,
        context=context,
    )
    account_request.save()
    return account_request


def get_pending_for_user(user):
    return AccountRequest.objects.filter(username=user.username).first()


def insert_write_access_request(
    user, organization, country, standard, standard_other, reason
):
    existing = get_pending_for_user(user)
    if existing is not None:
        return existing, False
    account_request = AccountRequest(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        organization=organization,
        country=country,
        standard=standard,
        standard_other=standard_other,
        reason=reason,
    )
    account_request.save()
    return account_request, True


def grant_write_access(user):
    from django.contrib.auth.models import Group
    from core_main_app.permissions import rights

    user.groups.add(Group.objects.get(name=rights.DEFAULT_GROUP))
    read_only_group = Group.objects.filter(name=rights.READ_ONLY_GROUP).first()
    if read_only_group is not None:
        user.groups.remove(read_only_group)


def _send_write_access_granted_email(user):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    if not user.email:
        return
    context = {"user": user, "URI": SERVER_URI}
    email = EmailMultiAlternatives(
        "Write access granted on AsphaltMine",
        render_to_string(
            "core_website_app/admin/email/write_access_granted.txt", context
        ),
        None,
        [user.email],
    )
    email.attach_alternative(
        render_to_string(
            "core_website_app/admin/email/write_access_granted.html", context
        ),
        "text/html",
    )
    email.send(fail_silently=True)


def accept(account_request):
    """Accept an account request"""
    user = None
    try:
        user = _get_user_by_username(account_request.username)
        user.is_active = True
        user.save()
        grant_write_access(user)
        _send_write_access_granted_email(user)
    finally:
        account_request.delete()
        if user is not None:
            return user

        raise ApiError("User does not exist")


def deny(account_request, send_email=True, email_params=None):
    """Delete an account request"""
    user = None
    try:
        user = _get_user_by_username(account_request.username)
    finally:
        account_request.delete()

        if send_email:
            account_request_email = account_request.email
            context = {
                "lastname": account_request.last_name,
                "firstname": account_request.first_name,
                "URI": SERVER_URI,
            }

            inline_template = (
                email_params.get("body") if email_params else None
            )

            if inline_template:
                send_mail_api.send_mail(
                    recipient_list=[account_request_email],
                    subject=email_params.get("subject")
                    if email_params
                    else EMAIL_DENY_SUBJECT,
                    body=inline_template,
                )
            else:
                send_mail_api.send_mail_from_template(
                    subject=email_params.get("subject")
                    if email_params
                    else EMAIL_DENY_SUBJECT,
                    recipient_list=[account_request_email],
                    path_to_template="core_website_app/admin/email/request_account_denied.html",
                    context=context,
                )
        if user is not None:
            return

        raise ApiError("User does not exist")


def _get_user_by_username(username):
    """Returns a user given its username"""
    return User.objects.get(username=username)


def _get_user_by_email(email):
    """Returns a user given its email"""
    return User.objects.get(email__iexact=email)


def _get_user_by_id(user_id):
    """Returns a user given its primary key"""
    return User.objects.get(pk=user_id)


def _create_and_save_user(username, password, first_name, last_name, email):
    """Save a user with the given parameters"""
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    user.save()
    return user
