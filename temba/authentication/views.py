import warnings

from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from smartmin.users.views import Login as SmartminLogin
from two_factor import signals
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.utils import backup_phones, default_device
from two_factor.views.utils import IdempotentSessionWizardView, class_view_decorator

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.auth.forms import AuthenticationForm
from django.forms import Form
from django.shortcuts import redirect, resolve_url
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class Login(IdempotentSessionWizardView, SmartminLogin):

    template_name = "two_factor/core/login.html"
    form_list = (("auth", AuthenticationForm), ("token", AuthenticationTokenForm), ("backup", BackupTokenForm))
    idempotent_dict = {"token": False, "backup": False}

    def has_token_step(self):
        return default_device(self.get_user())

    def has_backup_step(self):
        return default_device(self.get_user()) and "token" not in self.storage.validated_step_data

    condition_dict = {"token": has_token_step, "backup": has_backup_step}
    redirect_field_name = REDIRECT_FIELD_NAME

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None

    def post(self, *args, **kwargs):
        """
        The user can select a particular device to challenge, being the backup
        devices added to the account.
        """
        # Generating a challenge doesn't require to validate the form.
        if "challenge_device" in self.request.POST:
            return self.render_goto_step("token")

        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        login(self.request, self.get_user())

        redirect_to = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name, "")
        )

        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        device = getattr(self.get_user(), "otp_device", None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request, user=self.get_user(), device=device)
        return redirect(redirect_to)

    def get_form_kwargs(self, step=None):
        """
        AuthenticationTokenForm requires the user kwarg.
        """
        if step == "auth":
            return {"request": self.request}
        if step in ("token", "backup"):
            return {"user": self.get_user(), "initial_device": self.get_device(step)}
        return {}

    def get_device(self, step=None):
        """
        Returns the OTP device selected by the user, or his default device.
        """
        if not self.device_cache:
            challenge_device_id = self.request.POST.get("challenge_device", None)
            if challenge_device_id:
                for device in backup_phones(self.get_user()):
                    if device.persistent_id == challenge_device_id:
                        self.device_cache = device
                        break
            if step == "backup":
                try:
                    self.device_cache = self.get_user().staticdevice_set.get(name="backup")
                except StaticDevice.DoesNotExist:
                    pass
            if not self.device_cache:
                self.device_cache = default_device(self.get_user())
        return self.device_cache

    def render(self, form=None, **kwargs):
        """
        If the user selected a device, ask the device to generate a challenge;
        either making a phone call or sending a text message.
        """
        if self.steps.current == "token":
            self.get_device().generate_challenge()
        return super().render(form, **kwargs)

    def get_user(self):
        """
        Returns the user authenticated by the AuthenticationForm. Returns False
        if not a valid user; see also issue #65.
        """
        if not self.user_cache:
            form_obj = self.get_form(step="auth", data=self.storage.get_step_data("auth"))
            self.user_cache = form_obj.is_valid() and form_obj.user_cache
        return self.user_cache

    def get_context_data(self, form, **kwargs):
        """
        Adds user's default and backup OTP devices to the context.
        """
        context = super().get_context_data(form, **kwargs)
        context["allow_email_recovery"] = getattr(settings, "USER_ALLOW_EMAIL_RECOVERY", True)

        if self.steps.current == "token":
            context["device"] = self.get_device()
            context["other_devices"] = [
                phone for phone in backup_phones(self.get_user()) if phone != self.get_device()
            ]
            try:
                context["backup_tokens"] = self.get_user().staticdevice_set.get(name="backup").token_set.count()
            except StaticDevice.DoesNotExist:
                context["backup_tokens"] = 0

        if getattr(settings, "LOGOUT_REDIRECT_URL", None):
            context["cancel_url"] = resolve_url(settings.LOGOUT_REDIRECT_URL)
        elif getattr(settings, "LOGOUT_URL", None):
            warnings.warn(
                "LOGOUT_URL has been replaced by LOGOUT_REDIRECT_URL, please "
                "review the URL and update your settings.",
                DeprecationWarning,
            )
            context["cancel_url"] = resolve_url(settings.LOGOUT_URL)
        return context


@class_view_decorator(never_cache)
@class_view_decorator(otp_required)
class BackupTokensView(FormView):
    """
    View for listing and generating backup tokens.
    A user can generate a number of static backup tokens. When the user loses
    its phone, these backup tokens can be used for verification. These backup
    tokens should be stored in a safe location; either in a safe or underneath
    a pillow ;-).
    """

    form_class = Form
    success_url = "authentication.backup"
    template_name = "two_factor/core/backup_tokens.html"
    number_of_tokens = 10

    def get_device(self):
        return self.request.user.staticdevice_set.get_or_create(name="backup")[0]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device"] = self.get_device()
        return context

    def form_valid(self, form):
        """
        Delete existing backup codes and generate new ones.
        """
        device = self.get_device()
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        return redirect(self.success_url)
