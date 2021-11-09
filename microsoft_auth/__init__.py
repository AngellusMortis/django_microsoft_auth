"""
Simple app to enable Microsoft Account, Office 365 and Xbox Live authentcation as a
Django authentcation backend.
"""

__version__ = "2.4.1"

import django

# TODO: remove when dropping support for <3.2
if int(f"{django.VERSION[0]}{django.VERSION[1]}") < 32:
    default_app_config = "microsoft_auth.apps.MicrosoftAuthConfig"
