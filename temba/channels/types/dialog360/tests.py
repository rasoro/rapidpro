from unittest.mock import patch

from django_redis import get_redis_connection
from requests import RequestException

from django.forms import ValidationError
from django.urls import reverse

from temba.request_logs.models import HTTPLog
from temba.templates.models import Template, TemplateTranslation
from temba.tests import MockResponse, TembaTest

from ...models import Channel
from .tasks import refresh_360_templates
from .type import Dialog360Type


class Dialog360ClaimViewTest(TembaTest):
    def setUp(self):
        super().setUp()

        Channel.objects.all().delete()

        self.claim_url = reverse("channels.types.dialog360.claim")

    def test_claim(self):
        self.login(self.admin)

        # make sure 360dialog is on the claim page
        response = self.client.get(reverse("channels.channel_claim"), follow=True)
        self.assertContains(response, self.claim_url)

        response = self.client.get(self.claim_url)
        self.assertEqual(200, response.status_code)
        post_data = response.context["form"].initial

        post_data["number"] = "1234"
        post_data["country"] = "RW"
        post_data["base_url"] = "https://ilhasoft.com.br/whatsapp"
        post_data["api_key"] = "123456789"

        # will fail with invalid phone number
        response = self.client.post(self.claim_url, post_data)
        self.assertFormError(response, "form", None, ["Please enter a valid phone number"])

        # valid number
        post_data["number"] = "0788123123"

        # then success
        with patch("requests.post") as mock_post:
            mock_post.side_effect = [MockResponse(200, '{ "url": "https://ilhasoft.com.br/whatsapp" }')]

            response = self.client.post(self.claim_url, post_data)
            self.assertEqual(302, response.status_code)

        channel = Channel.objects.get()

        self.assertEqual("123456789", channel.config[Channel.CONFIG_AUTH_TOKEN])
        self.assertEqual("https://ilhasoft.com.br/whatsapp", channel.config[Channel.CONFIG_BASE_URL])

        self.assertEqual("+250788123123", channel.address)
        self.assertEqual("RW", channel.country)
        self.assertEqual("D3", channel.channel_type)
        self.assertEqual(45, channel.tps)
        self.assertTrue(channel.get_type().has_attachment_support(channel))

        # test activating the channel
        with patch("requests.post") as mock_post:
            mock_post.side_effect = [MockResponse(200, '{ "url": "https://ilhasoft.com.br/whatsapp" }')]

            Dialog360Type().activate(channel)
            self.assertEqual(
                mock_post.call_args_list[0][1]["json"]["url"],
                "https://%s%s"
                % (channel.org.get_brand_domain(), reverse("courier.d3", args=[channel.uuid, "receive"])),
            )

        with patch("requests.post") as mock_post:
            mock_post.side_effect = [MockResponse(400, '{ "meta": { "success": false } }')]

            try:
                Dialog360Type().activate(channel)
                self.fail("Should have thrown error activating channel")
            except ValidationError:
                pass

        # deactivate our channel
        with self.settings(IS_PROD=True):
            channel.release()
            self.assertFalse(channel.is_active)


class Dialog360TemplatesRefreshTest(TembaTest):
    def setUp(self):
        super().setUp()
        Channel.objects.all().delete()
        self.valid_channel = Channel.create(
            self.org,
            self.admin,
            "BR",
            "D3",
            name="360Dialog: Templates Refresh Test",
            address="1234",
            config={
                Channel.CONFIG_BASE_URL: "https://ilhasoft.com.br/whatsapp",
                Channel.CONFIG_AUTH_TOKEN: "123456789",
            },
        )
        self.invalid_channel = Channel.create(
            self.org,
            self.admin,
            "BR",
            "D3",
            name="360Dialog: Templates Refresh Test",
            address="1234",
            config={Channel.CONFIG_BASE_URL: "https://ilhasoft.com.br/whatsapp"},
        )

    def test_refresh_templates(self):
        self.login(self.admin)
        # test refresh_templates (same as channels.types.whatsapp.tests.WhatsAppTypeTest)
        with patch("requests.get") as mock_get:
            mock_get.side_effect = [
                RequestException("Network is unreachable", response=MockResponse(100, "")),
                Exception("Blah"),
                MockResponse(400, '{ "meta": { "success": false } }'),
                MockResponse(
                    200,
                    """
                    {
                        "count": 11,
                        "filters": {},
                        "limit": 1000,
                        "offset": 0,
                        "sort": ["id"],
                        "total": 11,
                        "waba_templates": [
                            {
                                "name": "hello",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "Hello {{1}}"
                                }
                                ],
                                "language": "en",
                                "status": "submitted",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "hello",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "Hi {{1}}"
                                }
                                ],
                                "language": "en_GB",
                                "status": "submitted",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "hello",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "Bonjour {{1}}"
                                }
                                ],
                                "language": "fr",
                                "status": "approved",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "goodbye",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "Goodbye {{1}}, see you on {{2}}. See you later {{1}}"
                                }
                                ],
                                "language": "en",
                                "status": "submitted",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "workout_activity",
                                "components": [
                                {
                                    "type": "HEADER",
                                    "text": "Workout challenge week extra points!"
                                },
                                {
                                    "type": "BODY",
                                    "text": "Hey {{1}}, Week {{2}} workout is out now. Get your discount of {{3}} for the next workout by sharing this program to 3 people."
                                },
                                {
                                    "type": "FOOTER",
                                    "text": "Remember to drink water."
                                }
                                ],
                                "language": "en",
                                "status": "submitted",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "workout_activity_with_unsuported_variablet",
                                "components": [
                                {
                                    "type": "HEADER",
                                    "text": "Workout challenge week {{2}}, {{4}} extra points!"
                                },
                                {
                                    "type": "BODY",
                                    "text": "Hey {{1}}, Week {{2}} workout is out now. Get your discount of {{3}} for the next workout by sharing this program to 3 people."
                                },
                                {
                                    "type": "FOOTER",
                                    "text": "Remember to drink water."
                                }
                                ],
                                "language": "en",
                                "status": "submitted",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "missing_text_component",
                                "components": [
                                {
                                    "type": "HEADER",
                                    "format": "IMAGE",
                                    "example": {
                                    "header_handle": ["FOO"]
                                    }
                                }
                                ],
                                "language": "en",
                                "status": "approved",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "invalid_component",
                                "components": [
                                {
                                    "type": "RANDOM",
                                    "text": "Bonjour {{1}}"
                                }
                                ],
                                "language": "fr",
                                "status": "approved",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "invalid_status",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "This is an unknown status, it will be ignored"
                                }
                                ],
                                "language": "en",
                                "status": "UNKNOWN",
                                "category": "ISSUE_RESOLUTION"
                            },
                            {
                                "name": "invalid_language",
                                "components": [
                                {
                                    "type": "BODY",
                                    "text": "This is an unknown language, it will be ignored"
                                }
                                ],
                                "language": "xyz",
                                "status": "approved",
                                "category": "ISSUE_RESOLUTION"
                            }
                        ]
                    }
                    """,
                ),
            ]

            # RequestException: check HTTPLog
            refresh_360_templates()
            self.assertEqual(1, HTTPLog.objects.filter(log_type=HTTPLog.WHATSAPP_TEMPLATES_SYNCED).count())

            # Exception: check logger
            with self.assertLogs("temba.channels.types.dialog360.tasks") as logger:
                refresh_360_templates()
                self.assertEqual(len(logger.output), 1)
                self.assertTrue("Error refresh dialog360 whatsapp templates" in logger.output[0])

            # should skip if fail with API
            refresh_360_templates()
            self.assertEqual(0, Template.objects.filter(org=self.org).count())
            self.assertEqual(0, TemplateTranslation.objects.filter(channel=self.valid_channel).count())

            # should skip if locked
            r = get_redis_connection()
            with r.lock("refresh_360_templates", timeout=1800):
                refresh_360_templates()
                self.assertEqual(0, Template.objects.filter(org=self.org).count())
                self.assertEqual(0, TemplateTranslation.objects.filter(channel=self.valid_channel).count())

            # now it should refresh
            refresh_360_templates()

            mock_get.assert_called_with(
                "https://ilhasoft.com.br/whatsapp/v1/configs/templates",
                headers={
                    "D360-Api-Key": self.valid_channel.config[Channel.CONFIG_AUTH_TOKEN],
                    "Content-Type": "application/json",
                },
            )

            # should have 4 templates
            self.assertEqual(4, Template.objects.filter(org=self.org).count())
            # and 7 translations
            self.assertEqual(6, TemplateTranslation.objects.filter(channel=self.valid_channel).count())
            # But None for invalid channels
            self.assertEqual(0, TemplateTranslation.objects.filter(channel=self.invalid_channel).count())

            # hit our template page
            response = self.client.get(reverse("channels.types.dialog360.templates", args=[self.valid_channel.uuid]))
            # should have our template translations
            self.assertContains(response, "Bonjour")
            self.assertContains(response, "Hello")
            self.assertContains(
                response, reverse("channels.types.dialog360.sync_logs", args=[self.valid_channel.uuid])
            )

            # Check if message templates link are in sync_logs view
            response = self.client.get(reverse("channels.types.dialog360.sync_logs", args=[self.valid_channel.uuid]))
            gear_links = response.context["view"].get_gear_links()
            self.assertEqual(gear_links[-1]["title"], "Message Templates")
            self.assertEqual(
                gear_links[-1]["href"], reverse("channels.types.dialog360.templates", args=[self.valid_channel.uuid])
            )
