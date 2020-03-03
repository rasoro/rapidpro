from django.conf import settings
from django.urls import reverse
from django.shortcuts import resolve_url

from django_otp.plugins.otp_totp.models import TOTPDevice
from smartmin.users.views import Login as SmartminLogin
from two_factor.views.core import LoginView

class Login(LoginView, SmartminLogin):

    template_name = 'smartmin/users/login.html'

    def get_success_url(self):
        url = self.get_redirect_url()
        user_two_factor_authentication = getattr(self.request.user.get_settings(), "two_factor_authentication")
        # org_two_factor_authentication = getattr(self.request.user.get_org(), "two_factor_authentication")
        # verify user with two_authentication and org with two_authentication
        if user_two_factor_authentication:
            return reverse("two_factor:profile")
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)
