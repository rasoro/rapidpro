import logging

import pytz
from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from temba.orgs.models import Org

LOGGER = logging.getLogger("connect_django_oidc")


class ConnectOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Custom authentication class for django-admin.
    """

    def verify_claims(self, claims):
        #validação de permissão
        print('foi aqui no verify_claims')
        verified = super(ConnectOIDCAuthenticationBackend, self).verify_claims(claims)
        is_admin = "admin" in claims.get("roles", [])
        return verified #and is_admin # not checking for user roles from keycloak at this time

    def create_user(self, claims):
        # Override existing create_user method in OIDCAuthenticationBackend
        print('foi aqui no create_user')
        email = claims.get('email')
        username = self.get_username(claims)
        user = self.UserModel.objects.create_user(email, username)

        old_username = user.username
        user.username = claims.get("preferred_username", old_username)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.email = claims.get("email", "")
        user.save()

        org = Org.objects.create(
            name="Temba New",
            timezone=pytz.timezone("Africa/Kigali"),
            brand=settings.DEFAULT_BRAND,
            created_by=user,
            modified_by=user,
        )
        org.administrators.add(user)

        # initialize our org, but without any credits
        org.initialize(branding=org.get_branding(), topup_size=0)

        return user

    def update_user(self, user, claims):
        print('foi aqui no update_user')
        print(claims)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.email = claims.get("email", "")
        user.save()

        return user
