from unittest import mock

from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.oath import totp
from two_factor.models import random_hex_str

from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from .utils import UserMixin


class LoginTest(UserMixin, TestCase):

    databases = ("default", "direct")

    def _post(self, data=None):
        return self.client.post(reverse("authentication.login"), data=data)

    def test_form(self):
        response = self.client.get(reverse("authentication.login"))
        self.assertContains(response, "Password:")

    def test_invalid_login(self):
        response = self._post({"auth-username": "unknown", "auth-password": "secret", "login-current_step": "auth"})
        self.assertContains(response, "Please enter a correct")
        self.assertContains(response, "and password.")

    @mock.patch("two_factor.views.core.signals.user_verified.send")
    def test_valid_login(self, mock_signal):
        self.create_user()
        response = self._post(
            {"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"}
        )
        self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

        # No signal should be fired for non-verified user logins.
        self.assertFalse(mock_signal.called)

    def test_valid_login_with_custom_redirect(self):
        redirect_url = reverse("authentication.setup")
        self.create_user()
        response = self.client.post(
            "%s?%s" % (reverse("authentication.login"), "next=" + redirect_url),
            {"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"},
        )
        self.assertRedirects(response, redirect_url)

    def test_valid_login_with_custom_post_redirect(self):
        redirect_url = reverse("authentication.setup")
        self.create_user()
        response = self._post(
            {
                "auth-username": "bouke@example.com",
                "auth-password": "secret",
                "login-current_step": "auth",
                "next": redirect_url,
            }
        )
        self.assertRedirects(response, redirect_url)

    @mock.patch("two_factor.views.core.signals.user_verified.send")
    def test_with_generator(self, mock_signal):
        user = self.create_user()
        device = user.totpdevice_set.create(name="default", key=random_hex_str())

        response = self._post(
            {"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"}
        )
        self.assertContains(response, "Token:")

        response = self._post({"token-otp_token": "123456", "login-current_step": "token"})
        self.assertEqual(
            response.context_data["wizard"]["form"].errors,
            {"__all__": ["Invalid token. Please make sure you " "have entered it correctly."]},
        )

        # reset throttle because we're not testing that
        device.throttle_reset()

        response = self._post({"token-otp_token": totp(device.bin_key), "login-current_step": "token"})
        self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

        self.assertEqual(device.persistent_id, self.client.session.get(DEVICE_ID_SESSION_KEY))

        # Check that the signal was fired.
        mock_signal.assert_called_with(sender=mock.ANY, request=mock.ANY, user=user, device=device)

    @mock.patch("two_factor.views.core.signals.user_verified.send")
    def test_throttle_with_generator(self, mock_signal):
        user = self.create_user()
        device = user.totpdevice_set.create(name="default", key=random_hex_str())

        self._post({"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"})

        # throttle device
        device.throttle_increment()

        response = self._post({"token-otp_token": totp(device.bin_key), "login-current_step": "token"})
        self.assertEqual(
            response.context_data["wizard"]["form"].errors,
            {"__all__": ["Invalid token. Please make sure you " "have entered it correctly."]},
        )

    @mock.patch("two_factor.views.core.signals.user_verified.send")
    def test_with_backup_token(self, mock_signal):
        user = self.create_user()
        user.totpdevice_set.create(name="default", key=random_hex_str())
        device = user.staticdevice_set.create(name="backup")
        device.token_set.create(token="abcdef123")

        # Backup phones should be listed on the login form
        response = self._post(
            {"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"}
        )
        self.assertContains(response, "Backup Token")

        # Should be able to go to backup tokens step in wizard
        response = self._post({"wizard_goto_step": "backup"})
        self.assertContains(response, "backup tokens")

        # Wrong codes should not be accepted
        response = self._post({"backup-otp_token": "WRONG", "login-current_step": "backup"})
        self.assertEqual(
            response.context_data["wizard"]["form"].errors,
            {"__all__": ["Invalid token. Please make sure you " "have entered it correctly."]},
        )

        # Valid token should be accepted.
        response = self._post({"backup-otp_token": "abcdef123", "login-current_step": "backup"})
        self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

        # Check that the signal was fired.
        mock_signal.assert_called_with(sender=mock.ANY, request=mock.ANY, user=user, device=device)

    @mock.patch("two_factor.views.utils.logger")
    def test_login_different_user_on_existing_session(self, mock_logger):
        """
        This test reproduces the issue where a user is logged in and a different user
        attempts to login.
        """
        self.create_user()
        self.create_user(username="vedran@example.com")

        response = self._post(
            {"auth-username": "bouke@example.com", "auth-password": "secret", "login-current_step": "auth"}
        )
        self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

        response = self._post(
            {"auth-username": "vedran@example.com", "auth-password": "secret", "login-current_step": "auth"}
        )
        self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

    def test_missing_management_data(self):
        # missing management data
        response = self._post({"auth-username": "bouke@example.com", "auth-password": "secret"})

        # view should return HTTP 400 Bad Request
        self.assertEqual(response.status_code, 400)


class BackupTokensTest(UserMixin, TestCase):

    databases = ("default", "direct")

    def setUp(self):
        super().setUp()
        self.create_user()
        self.enable_otp()
        self.login_user()

    def test_empty(self):
        response = self.client.get(reverse("authentication.backup"))
        self.assertContains(response, "You don't have any backup codes yet.")

    def test_generate(self):
        url = reverse("authentication.backup")

        response = self.client.post(url)
        self.assertRedirects(response, url)

        response = self.client.get(url)
        first_set = set([token.token for token in response.context_data["device"].token_set.all()])
        self.assertNotContains(response, "You don't have any backup codes " "yet.")
        self.assertEqual(10, len(first_set))

        # Generating the tokens should give a fresh set
        self.client.post(url)
        response = self.client.get(url)
        second_set = set([token.token for token in response.context_data["device"].token_set.all()])
        self.assertNotEqual(first_set, second_set)
