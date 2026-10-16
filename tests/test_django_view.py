import json
from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-secret-key",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.staticfiles",
            "biocore_feedback",
        ],
        ROOT_URLCONF="biocore_feedback.urls",
        STATIC_URL="/static/",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        SLACK_WEBHOOK_URL="https://example.com/mock-webhook",
        BIOCORE_FEEDBACK_RATE_LIMIT=10,
    )
    import django
    django.setup()

from biocore_feedback.views import submit_feedback


class BiocoreFeedbackDjangoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("biocore_feedback.views.send_to_slack_sync")
    def test_submit_success(self, mock_slack):
        mock_slack.return_value = None
        payload = {
            "name": "Maria",
            "app": "Genomics Apps",
            "message": "Testing Django package",
            "page_url": "http://localhost:8000/",
        }
        request = self.factory.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = submit_feedback(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["ok"])
        self.assertTrue(mock_slack.called)

    def test_submit_empty_message(self):
        payload = {"name": "Maria", "app": "Genomics Apps", "message": ""}
        request = self.factory.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = submit_feedback(request)
        self.assertEqual(response.status_code, 400)

    def test_submit_empty_name(self):
        payload = {"name": "", "app": "Genomics Apps", "message": "hello"}
        request = self.factory.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        response = submit_feedback(request)
        self.assertEqual(response.status_code, 400)
