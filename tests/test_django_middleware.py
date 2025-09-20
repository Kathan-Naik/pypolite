import json
import django
from django.conf import settings
from django.http import JsonResponse
from django.test import SimpleTestCase, Client
from django.urls import path
from django.views import View
from pypolite.django_middleware import PyPoliteDjangoMiddleware

# --- Configure minimal Django settings for tests ---
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test",
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
            "pypolite.django_middleware.PyPoliteDjangoMiddleware",
        ],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        PYPOLITE_WORDS=["idiot", "stupid"],      # profanity list for test
        PYPOLITE_FIELDS=["message"],
        PYPOLITE_ENDPOINTS=["/echo/"],             # fields to check
    )
    django.setup()

# --- Minimal test view ---
class EchoView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        return JsonResponse({"received": data})

# Additional view for not-included endpoint
class OtherView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        return JsonResponse({"received": data})

# --- URL configuration for tests ---
urlpatterns = [
    path("echo/", EchoView.as_view()),
    path("other/", OtherView.as_view()),
]

# --- Test Case ---
class PyPoliteMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_allows_clean_message(self):
        """Test that a clean message passes"""
        response = self.client.post(
            "/echo/",
            data=json.dumps({"message": "Hello friend!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["received"]["message"], "Hello friend!")


    def test_not_included_endpoint_passes(self):
        """Test that requests to endpoints not in PYPOLITE_ENDPOINTS are allowed"""
        response = self.client.post(
            "/other/",
            data=json.dumps({"message": "You are stupid!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["received"]["message"], "You are stupid!")

    def test_blocks_profanity(self):
        """Test that a profane message is blocked"""
        response = self.client.post(
            "/echo/",
            data=json.dumps({"message": "You are stupid!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Profanity detected", response.json()["error"])
