================
Core Website App
================

Basic web functionalities for the curator core project.

Quickstart
==========

1. Add "core_website_app" to your INSTALLED_APPS setting
--------------------------------------------------------

.. code:: python

    INSTALLED_APPS = [
        ...
        'core_website_app',
    ]

2. Include the core_website_app URLconf in your project urls.py
---------------------------------------------------------------

.. code:: python

    url(r'^website/', include('core_website_app.urls')),


3. Install and configure Captcha
--------------------------------

See instructions: https://django-simple-captcha.readthedocs.io/en/latest/usage.html#installation
