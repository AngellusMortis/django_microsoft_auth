import json
import re

from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.middleware.csrf import (CSRF_TOKEN_LENGTH, _compare_salted_tokens,
                                    get_token)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt


class AuthenticateCallbackView(View):
    """ Authentication callback for Microsoft to call as part of OAuth2
            implicit grant flow

        For more details:
        https://developer.microsoft.com/en-us/graph/docs/get-started/rest
    """

    messages = {
        'bad_state': _('An invalid state variable was provided. '
                       'Please refresh the page and try again later.'),
        'missing_code': _('No authentication code was provided from '
                          'Microsoft. Please try again.'),
        'login_failed': _('Failed to authenticate you for an unknown reason. '
                          'Please try again later.'),
    }

    # manually mark methods csrf_exempt to handle CSRF processing ourselves
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super() \
            .dispatch(request, *args, **kwargs)

    def post(self, request):
        """ main callback for Microsoft to call

            validates Microsoft response, attempts to authenticate user and
            returns simple HTML page with Javascript that will post a message
            to parent window with details of result """

        domain = Site.objects.get_current().domain
        context = {
            'base_url': 'https://{0}/'.format(domain),
            'message': {}}

        # validates state using Django CSRF system
        valid_csrf = False
        if 'state' in request.POST:
            request_token = request.POST['state']
            # validate format of CSRF token
            if re.search('[a-zA-Z0-9]', request_token) and \
                    len(request_token) == CSRF_TOKEN_LENGTH:
                # validate CSRF token
                if _compare_salted_tokens(request_token, get_token(request)):
                    valid_csrf = True

        if not valid_csrf:
            context['message'] = {'error': 'bad_state'}
        else:
            # handle error message from Microsoft
            if 'error' in request.POST:
                context['message'] = {
                    'error': request.POST['error'],
                    'error_description': request.POST['error_description']}
            # validate existance of Microsoft authentication code
            elif 'code' not in request.POST:
                context['message'] = {'error': 'missing_code'}
            else:
                # authenticate user using Microsoft code
                user = authenticate(request, code=request.POST['code'])
                if user is None:
                    # this should not fail at this point except for network
                    # error while retrieving profile or database error
                    # adding new user
                    context['message'] = {'error': 'login_failed'}
                else:
                    login(request, user)

        status_code = 200
        if 'error' in context['message']:
            if 'error_description' not in context['message']:
                context['message']['error_description'] = \
                    self.messages[context['message']['error']]
            status_code = 400

        context['message'] = mark_safe(json.dumps(context['message']))

        return render(
            request, 'microsoft/auth_callback.html',
            context, status=status_code)
