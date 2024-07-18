""" Menus
"""

from django.urls import reverse
from menu import Menu, MenuItem

from core_website_app.settings import (
    DISPLAY_PRIVACY_POLICY_FOOTER,
    DISPLAY_TERMS_OF_USE_FOOTER,
    DISPLAY_CONTACT_FOOTER,
    DISPLAY_HELP_FOOTER,
    DISPLAY_RULES_OF_BEHAVIOR_FOOTER,
)

if DISPLAY_PRIVACY_POLICY_FOOTER:
    Menu.add_item(
        "footer",
        MenuItem(
            "Privacy policy", reverse("core_website_app_privacy"), weight=1001
        ),
    )
if DISPLAY_TERMS_OF_USE_FOOTER:
    Menu.add_item(
        "footer",
        MenuItem(
            "Terms of use", reverse("core_website_app_terms"), weight=1002
        ),
    )
if DISPLAY_CONTACT_FOOTER:
    Menu.add_item(
        "footer",
        MenuItem(
            "Contact",
            "https://asphaltmine.org/contact-us/",
            icon="envelope",
            weight=1003,
        ),
    )
if DISPLAY_HELP_FOOTER:
    Menu.add_item(
        "footer",
        MenuItem(
            "Help",
            reverse("core_website_app_help"),
            icon="question-circle",
            weight=1004,
        ),
    )
if DISPLAY_RULES_OF_BEHAVIOR_FOOTER:
    Menu.add_item(
        "footer",
        MenuItem(
            "Rules of Behavior",
            reverse("core_website_app_rules_of_behavior"),
            icon="balance-scale",
            weight=1004,
        ),
    )

# Admin menus for website app
website_children = (
    MenuItem(
        "Privacy Policy",
        reverse("core-admin:core_website_app_privacy"),
        icon="user-secret",
    ),
    MenuItem(
        "Terms of Use",
        reverse("core-admin:core_website_app_terms"),
        icon="file-alt",
    ),
    MenuItem(
        "Help Page",
        reverse("core-admin:core_website_app_help"),
        icon="question-circle",
    ),
    MenuItem(
        "Rules of Behavior",
        reverse("core-admin:core_website_app_rules_of_behavior"),
        icon="balance-scale",
    ),
    MenuItem(
        "User requests",
        reverse("core-admin:core_website_app_user_requests"),
        icon="user-plus",
        item_count_url="core-admin:core_website_app_request_count",
    ),
    MenuItem(
        "Contact messages",
        reverse("core-admin:core_website_app_contact_messages"),
        icon="envelope",
        item_count_url="core-admin:core_website_app_message_count",
    ),
)

Menu.add_item(
    "admin",
    MenuItem("WEBSITE", None, children=website_children, weight=-10000),
)
