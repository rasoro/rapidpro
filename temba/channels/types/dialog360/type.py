import requests

from django.conf.urls import url
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from temba.channels.models import Channel
from temba.channels.types.dialog360.views import ClaimView, SyncLogsView, TemplatesView
from temba.contacts.models import URN
from temba.templates.models import TemplateTranslation

from ...models import ChannelType

STATUS_MAPPING = dict(
    submitted=TemplateTranslation.STATUS_PENDING,
    approved=TemplateTranslation.STATUS_APPROVED,
    rejected=TemplateTranslation.STATUS_REJECTED,
)


class Dialog360Type(ChannelType):
    """
    A 360 Dialog Channel Type
    """

    extra_links = [dict(name=_("Message Templates"), link="channels.types.dialog360.templates")]

    code = "D3"
    category = ChannelType.Category.SOCIAL_MEDIA

    courier_url = r"^d3/(?P<uuid>[a-z0-9\-]+)/(?P<action>receive)$"

    name = "360Dialog WhatsApp"
    icon = "icon-whatsapp"

    claim_blurb = _(
        "Activate your own enterprise WhatsApp account in %(link)s to communicate with your contacts. "
    ) % {"link": '<a href="https://www.360dialog.com/">360Dialog</a>'}
    claim_view = ClaimView

    schemes = [URN.WHATSAPP_SCHEME]
    max_length = 4096
    attachment_support = True

    def get_urls(self):
        return [
            self.get_claim_url(),
            url(r"^(?P<uuid>[a-z0-9\-]+)/templates$", TemplatesView.as_view(), name="templates"),
            url(r"^(?P<uuid>[a-z0-9\-]+)/sync_logs$", SyncLogsView.as_view(), name="sync_logs"),
        ]

    def activate(self, channel):
        domain = channel.org.get_brand_domain()
        headers = {"D360-API-KEY": channel.config[Channel.CONFIG_AUTH_TOKEN], "Content-Type": "application/json"}

        # first set our callbacks
        payload = {"url": "https://" + domain + reverse("courier.d3", args=[channel.uuid, "receive"])}
        resp = requests.post(
            channel.config[Channel.CONFIG_BASE_URL] + "/v1/configs/webhook", json=payload, headers=headers
        )

        if resp.status_code != 200:
            raise ValidationError(_("Unable to register callbacks: %(resp)s"), params={"resp": resp.content})
