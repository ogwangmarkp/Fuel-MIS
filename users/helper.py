import jwt
from rest_framework import exceptions
from users.models import UserSession
from django.utils.translation import gettext as _
from rest_framework_jwt.settings import api_settings
from kwani_api.utils import set_logged_in_user_key
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import (
    get_authorization_header
)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Perform custom authentication logic here
        
        # For example, you might want to check a custom header
        token_expired = True
        auth_header = self.get_header(request)
        if auth_header is None:
            return None
        
        try:
            token = self.get_raw_token(auth_header)
            if token is None:
                raise exceptions.AuthenticationFailed('Token expired')
        except AuthenticationFailed:
            return None

        validated_token = self.get_validated_token(token)
        user = self.get_user(validated_token)
        if user is None:
            raise AuthenticationFailed('Invalid User Session')
        
        user_session = UserSession.objects.filter(user=user,session_token=validated_token).first()
        if user_session:
            token_expired = False
            set_logged_in_user_key(user_session.session_token)
           
        if token_expired:
            raise exceptions.AuthenticationFailed('Signature has expired.')
    
        return (user, token)
    

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()
        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if str(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        return auth[1]
        