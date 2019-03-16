import json
import logging
import re

from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.middleware.csrf import (
    CSRF_TOKEN_LENGTH,
    _compare_salted_tokens,
    get_token,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .conf import config
from .utils import get_scheme

logger = logging.getLogger("django")


class AuthenticateCallbackView(View):
    """ Authentication callback for Microsoft to call as part of OAuth2
            implicit grant flow

        For more details:
        https://developer.microsoft.com/en-us/graph/docs/get-started/rest
    """

    messages = {
        "bad_state": _(
            "An invalid state variable was provided. "
            "Please refresh the page and try again later."
        ),
        "missing_code": _(
            "No authentication code was provided from "
            "Microsoft. Please try again."
        ),
        "login_failed": _(
            "Failed to authenticate you for an unknown reason. "
            "Please try again later."
        ),
    }

    # manually mark methods csrf_exempt to handle CSRF processing ourselves
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        domain = Site.objects.get_current().domain

        scheme = get_scheme(self.request)

        self.context = {
            "base_url": "{0}://{1}/".format(scheme, domain),
            "message": {},
        }

        # validates state using Django CSRF system
        self._check_csrf(kwargs.get("state"))

        # validates response from Microsoft
        self._check_microsoft_response(
            kwargs.get("error"), kwargs.get("error_description")
        )

        # validates the code param and logs user in
        self._authenticate(kwargs.get("code"))

        # populates error_description if it does not exist yet
        if (
            "error" in self.context["message"]
            and "error_description" not in self.context["message"]
        ):
            self.context["message"]["error_description"] = self.messages[
                self.context["message"]["error"]
            ]

        self.context["message"] = mark_safe(
            json.dumps(self.context["message"])
        )
        return self.context

    def _check_csrf(self, state):
        # CSRF validation does not work with http
        if config.DEBUG and self.request.scheme == "http":
            return

        if state is None:
            state = ""

        csrf_token = get_token(self.request)
        checks = (
            re.search("[a-zA-Z0-9]", state),
            len(state) == CSRF_TOKEN_LENGTH,
            _compare_salted_tokens(state, csrf_token),
        )

        # validate state parameter
        if not all(checks):
            logger.debug("State validation failed:")
            logger.debug(f"state: {state}")
            logger.debug(f"csrf_token: {csrf_token}")
            logger.debug(f"checks: {checks}")
            self.context["message"] = {"error": "bad_state"}

    def _check_microsoft_response(self, error, error_description):
        if "error" not in self.context["message"]:
            if error is not None:
                self.context["message"] = {
                    "error": error,
                    "error_description": error_description,
                }

    def _authenticate(self, code):
        if "error" not in self.context["message"]:
            if code is None:
                self.context["message"] = {"error": "missing_code"}
            else:
                # authenticate user using Microsoft code
                user = authenticate(self.request, code=code)
                if user is None:
                    # this should not fail at this point except for network
                    # error while retrieving profile or database error
                    # adding new user
                    self.context["message"] = {"error": "login_failed"}
                else:
                    login(self.request, user)

    def post(self, request):
        """ main callback for Microsoft to call

            validates Microsoft response, attempts to authenticate user and
            returns simple HTML page with Javascript that will post a message
            to parent window with details of result """

        context = self.get_context_data(**request.POST.dict())

        status_code = 200
        if "error" in context["message"]:
            status_code = 400

        return render(
            request,
            "microsoft/auth_callback.html",
            context,
            status=status_code,
        )
