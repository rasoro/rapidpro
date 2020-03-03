from django.conf.urls import url

from .views import Login


urlpatterns = [
    url(r"^$", Login.as_view(), name="authentication.login"),
]
