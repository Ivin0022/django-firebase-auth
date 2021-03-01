from django.contrib.auth import get_user_model, login
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from firebase_admin import auth as firebase_auth
from .firebase_app import firebase_app

User = get_user_model()


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Firebase Authentication based django restframework authentication class.

    Clients should authenticate by passing a Firebase ID Token in the
    "Authorization" HTTP header, preprended with the string "<keyword> " where
    <keyword> is this classes `keyword` string property. For example:

    Authorization:Firebase xxxxx.yyyyy.zzzzz
    """

    keyword = 'Firebase'
    check_revoked = False

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)

        try:
            firebase_token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(firebase_token)

    def authenticate_credentials(self, firebase_token):
        try:
            decoded_token = firebase_auth.verify_id_token(
                firebase_token,
                app=firebase_app,
                check_revoked=self.check_revoked,
            )
        except (ValueError, firebase_auth.InvalidIdTokenError):
            # Token was either not a string or empty or not an valid Firebase ID token
            msg = 'The Firebase token was invalid.'
            raise AuthenticationFailed(msg)
        except firebase_auth.ExpiredIdTokenError:
            msg = 'The Firebase token has expired.'
            raise AuthenticationFailed(msg)
        except firebase_auth.RevokedIdTokenError:
            msg = 'The Firebase token has been revoked.'
            raise AuthenticationFailed(msg)
        except firebase_auth.CertificateFetchError:
            msg = 'Temporarily unable to verify the ID token.'
            raise AuthenticationFailed(msg)

        firebase_user_record = firebase_auth.get_user(
            decoded_token['uid'],
            app=firebase_app,
        )

        try:
            user = User.objects.get(uid=firebase_user_record.uid)
        except User.DoesNotExist:
            """
            making sure the user doesn't already exist with a different uid
            """
            user = self._create_user(firebase_user_record)

        if user is None:
            msg = 'Authentication credentials were not provided.'
            raise AuthenticationFailed(msg)

        return (user, decoded_token)

    def authenticate_header(self, request):
        """
        Returns a string that will be used as the value of the WWW-Authenticate
        header in a HTTP 401 Unauthorized response.
        """
        return self.keyword

    def _create_user(self, firebase_user_record):
        try:
            return User.objects.create_user(
                uid=firebase_user_record.uid,
                phone_number=firebase_user_record.phone_number,
                email=firebase_user_record.email,
                display_name=firebase_user_record.display_name,
            )
        except IntegrityError as e:
            raise AuthenticationFailed(e.args)
