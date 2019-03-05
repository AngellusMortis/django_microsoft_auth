#!/usr/bin/env python
import os
import sys


def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.site.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if "runserver" in sys.argv:
        os.environ["DEBUG_SKIP_THREAD"] = "1"
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    manage()
