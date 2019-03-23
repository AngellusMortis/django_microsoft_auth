import importlib
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .client import MicrosoftClient
from .conf import LOGIN_TYPE_XBL
from .models import MicrosoftAccount, XboxLiveAccount

logger = logging.getLogger("django")
User = get_user_model()


class MicrosoftAuthenticationBackend(ModelBackend):
    """ Authentication backend to authenticate a user against their Microsoft
        Uses Microsoft's Graph OAuth and XBL servers to authentiate. """

    config = None
    microsoft = None

    def __init__(self, user=None):
        from .conf import config

        self.config = config

    def authenticate(self, request, code=None):
        """
            Authenticates the user against the Django backend
                using a Microsoft auth code from
            https://login.microsoftonline.com/common/oauth2/v2.0/authorize or
            https://login.live.com/oauth20_authorize.srf

            For more details:
            https://developer.microsoft.com/en-us/graph/docs/get-started/rest
        """

        self.microsoft = MicrosoftClient(request=request)

        user = None
        if code is not None:
            # fetch OAuth token
            token = self.microsoft.fetch_token(code=code)

            # validate permission scopes
            if "access_token" in token and self.microsoft.valid_scopes(
                token["scope"]
            ):
                user = self._authenticate_user()

        if user is not None:
            self._call_hook(user)

        return user

    def _authenticate_user(self):
        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            return self._authenticate_xbox_user()
        else:
            return self._authenticate_microsoft_user()

    def _authenticate_xbox_user(self):
        xbox_token = self.microsoft.fetch_xbox_token()

        if "Token" in xbox_token:
            response = self.microsoft.get_xbox_profile()
            return self._get_user_from_xbox(response)
        return None

    def _authenticate_microsoft_user(self):
        claims = self.microsoft.get_claims()

        if claims is not None:
            return self._get_user_from_microsoft(claims)

        return None

    def _get_user_from_xbox(self, data):
        """ Retrieves existing Django user or creates
            a new one from Xbox Live profile data """
        user = None
        xbox_user = self._get_xbox_user(data)

        if xbox_user is not None:
            self._verify_xbox_user(xbox_user)

            user = xbox_user.user

            if (
                self.config.MICROSOFT_AUTH_XBL_SYNC_USERNAME
                and user.username != xbox_user.gamertag
            ):
                user.username = xbox_user.gamertag
                user.save()

        return user

    def _get_xbox_user(self, data):
        xbox_user = None

        try:
            xbox_user = XboxLiveAccount.objects.get(xbox_id=data["xid"])
            # update Gamertag since they can change over time
            if xbox_user.gamertag != data["gtg"]:
                xbox_user.gamertag = data["gtg"]
                xbox_user.save()
        except XboxLiveAccount.DoesNotExist:
            if self.config.MICROSOFT_AUTH_AUTO_CREATE:
                # create new Xbox Live Account
                xbox_user = XboxLiveAccount(
                    xbox_id=data["xid"], gamertag=data["gtg"]
                )
                xbox_user.save()

        return xbox_user

    def _verify_xbox_user(self, xbox_user):
        if xbox_user.user is None:
            user = User(username=xbox_user.gamertag)
            user.save()

            xbox_user.user = user
            xbox_user.save()

    def _get_user_from_microsoft(self, data):
        """ Retrieves existing Django user or creates
            a new one from Xbox Live profile data """
        user = None
        microsoft_user = self._get_microsoft_user(data)

        if microsoft_user is not None:
            user = self._verify_microsoft_user(microsoft_user, data)

        return user

    def _get_microsoft_user(self, data):
        microsoft_user = None

        try:
            microsoft_user = MicrosoftAccount.objects.get(
                microsoft_id=data["sub"]
            )
        except MicrosoftAccount.DoesNotExist:
            if self.config.MICROSOFT_AUTH_AUTO_CREATE:
                # create new Microsoft Account
                microsoft_user = MicrosoftAccount(microsoft_id=data["sub"])
                microsoft_user.save()

        return microsoft_user

    def _verify_microsoft_user(self, microsoft_user, data):
        user = microsoft_user.user

        if user is None:
            fullname = data.get("name")
            first_name, last_name = "", ""
            if fullname is not None:
                first_name, last_name = data["name"].split(" ", 1)

            try:
                # create new Django user from provided data
                user = User.objects.get(email=data["email"])

                if user.first_name == "" and user.last_name == "":
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
            except User.DoesNotExist:
                user = User(
                    username=data["preferred_username"][:150],
                    first_name=first_name,
                    last_name=last_name,
                    email=data["email"],
                )
                user.save()

            existing_account = self._get_existing_microsoft_account(user)
            if existing_account is not None:
                if self.config.MICROSOFT_AUTH_AUTO_REPLACE_ACCOUNTS:
                    existing_account.user = None
                    existing_account.save()
                else:
                    logger.warn(
                        "User {} already has linked Microsoft account".format(
                            user.email
                        )
                    )
                    return None

            microsoft_user.user = user
            microsoft_user.save()

        return user

    def _get_existing_microsoft_account(self, user):
        try:
            return MicrosoftAccount.objects.get(user=user)
        except MicrosoftAccount.DoesNotExist:
            return None

    def _call_hook(self, user):
        if self.config.MICROSOFT_AUTH_AUTHENTICATE_HOOK != "":
            hook_path = self.config.MICROSOFT_AUTH_AUTHENTICATE_HOOK
            module_path, function_name = hook_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)

            if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
                function(user, self.microsoft.xbox_token)
            else:
                function(user, self.microsoft.token)
