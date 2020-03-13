from two_factor.views import BackupTokensView, DisableView, ProfileView, QRGeneratorView, SetupCompleteView, SetupView

from django.conf.urls import url

from .views import Login

urlpatterns = [
    url(r"^login/$", Login.as_view(), name="authentication.login"),
    url(r"^two_factor/setup/$", SetupView.as_view(), name="authentication.setup"),
    url(r"^two_factor/qrcode/$", QRGeneratorView.as_view(), name="authentication.qr"),
    url(r"^two_factor/setup/complete/$", SetupCompleteView.as_view(), name="authentication.setup_complete"),
    url(r"^two_factor/backup/tokens/$", BackupTokensView.as_view(), name="authentication.backup"),
    url(r"^two_factor/profile/$", ProfileView.as_view(), name="authentication.profile"),
    url(r"^two_factor/disable/$", DisableView.as_view(), name="authentication.disable"),
]
