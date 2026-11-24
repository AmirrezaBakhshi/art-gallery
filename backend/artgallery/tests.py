import hashlib
from datetime import timedelta
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Gallary
from .authentication import token_digest


class GalleryAuthenticationTests(APITestCase):
    def signup(self, username):
        return self.client.post("/api/gallaries/", {
            "username": username,
            "password": "StrongPass123",
            "name": f"{username} Gallery",
            "email": f"{username}@example.com",
        }, format="json")

    def test_signup_hashes_password_and_sets_httponly_cookie(self):
        response = self.signup("gallery-one")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("token", response.data)
        self.assertTrue(response.cookies["gallery_session"]["httponly"])
        self.assertNotIn("password", response.data["gallery"])
        gallery = Gallary.objects.get(username="gallery-one")
        self.assertNotEqual(gallery.password, "StrongPass123")
        self.assertNotEqual(gallery.api_token, response.cookies["gallery_session"].value)

    def test_login_sets_httponly_cookie_for_valid_credentials(self):
        self.signup("gallery-two")
        response = self.client.post("/api/auth/login/", {
            "username": "gallery-two",
            "password": "StrongPass123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.cookies["gallery_session"].value)
        self.assertNotIn("token", response.data)

    def test_invalid_login_is_rejected(self):
        self.signup("gallery-three")
        response = self.client.post("/api/auth/login/", {
            "username": "gallery-three",
            "password": "incorrect",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_item_creation_requires_authentication_and_uses_authenticated_owner(self):
        self.client.cookies.clear()
        response = self.client.post("/api/items/", {"title": "Public artwork"}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        signup = self.signup("gallery-four")
        response = self.client.post("/api/items/", {"title": "Owned artwork"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["gallary_id"], signup.data["gallery"]["id"])

    def test_gallery_list_does_not_expose_password_or_token(self):
        self.signup("gallery-five")
        response = self.client.get("/api/gallaries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data[0])
        self.assertNotIn("api_token", response.data[0])

    def test_gallery_cannot_modify_another_gallery_item(self):
        first = self.signup("gallery-six")
        created = self.client.post("/api/items/", {"title": "First gallery item"}, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)

        self.client.cookies["gallery_session"] = self.signup("gallery-seven").cookies["gallery_session"].value
        response = self.client.patch(
            f"/api/items/{created.data['id']}/",
            {"title": "Hijacked title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_revokes_the_current_cookie(self):
        signup = self.signup("gallery-logout")
        old_token = signup.cookies["gallery_session"].value
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("gallery_session", response.cookies)
        self.client.cookies["gallery_session"] = old_token
        denied = self.client.post("/api/items/", {"title": "Should fail"}, format="json")
        self.assertIn(denied.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_legacy_plaintext_password_is_rejected_without_migration(self):
        Gallary.objects.create(
            username="legacy-gallery",
            password="LegacyPass123",
            name="Legacy Gallery",
            email="legacy@example.com",
        )
        response = self.client.post("/api/auth/login/", {
            "username": "legacy-gallery",
            "password": "LegacyPass123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_session_token_is_rejected(self):
        self.signup("gallery-expired")
        gallery = Gallary.objects.get(username="gallery-expired")
        gallery.api_token_expires_at = timezone.now() - timedelta(seconds=1)
        gallery.save(update_fields=["api_token_expires_at"])
        response = self.client.post("/api/items/", {"title": "Expired session"}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_cookie_authenticated_mutations_require_csrf(self):
        raw_token = "csrf-test-token-with-enough-randomness"
        gallery = Gallary.objects.create(
            username="gallery-csrf",
            password="unused",
            api_token=token_digest(raw_token),
            api_token_expires_at=timezone.now() + timedelta(days=1),
            name="CSRF Gallery",
            email="csrf@example.com",
        )
        client = APIClient(enforce_csrf_checks=True)
        client.cookies["gallery_session"] = raw_token
        denied = client.post("/api/items/", {"title": "Missing CSRF"}, format="json")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        client.get("/api/auth/csrf/")
        csrf_token = client.cookies["csrftoken"].value
        allowed = client.post(
            "/api/items/",
            {"title": "CSRF protected"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(allowed.status_code, status.HTTP_201_CREATED)
        self.assertEqual(allowed.data["gallary_id"], gallery.id)

    def test_csrf_bootstrap_returns_a_masked_token(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["csrfToken"])
        self.assertIn("csrftoken", response.cookies)

    def test_invalid_existing_cookie_does_not_block_login(self):
        self.signup("gallery-stale-login")
        client = APIClient()
        client.cookies["gallery_session"] = "invalid-stale-session"
        response = client.post("/api/auth/login/", {
            "username": "gallery-stale-login",
            "password": "StrongPass123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.cookies["gallery_session"].value)

    def test_invalid_existing_cookie_does_not_block_signup(self):
        client = APIClient()
        client.cookies["gallery_session"] = "invalid-stale-session"
        response = client.post("/api/gallaries/", {
            "username": "gallery-stale-signup",
            "password": "StrongPass123",
            "name": "Stale Cookie Gallery",
            "email": "stale-signup@example.com",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.cookies["gallery_session"].value)

    def test_login_uses_configured_session_lifetime(self):
        from django.test import override_settings
        self.signup("gallery-session-ttl")
        with override_settings(GALLERY_SESSION_TTL_DAYS=3):
            response = self.client.post("/api/auth/login/", {
                "username": "gallery-session-ttl",
                "password": "StrongPass123",
            }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        gallery = Gallary.objects.get(username="gallery-session-ttl")
        self.assertAlmostEqual(
            (gallery.api_token_expires_at - timezone.now()).total_seconds(),
            3 * 86400,
            delta=5,
        )
        self.assertEqual(int(response.cookies["gallery_session"]["max-age"]), 3 * 86400)

    def test_signup_requires_csrf_protection(self):
        client = APIClient(enforce_csrf_checks=True)
        payload = {
            "username": "gallery-csrf-signup",
            "password": "StrongPass123",
            "name": "CSRF Signup",
            "email": "csrf-signup@example.com",
        }
        denied = client.post("/api/gallaries/", payload, format="json")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        bootstrap = client.get("/api/auth/csrf/")
        token = bootstrap.data["csrfToken"]
        allowed = client.post(
            "/api/gallaries/",
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(allowed.status_code, status.HTTP_201_CREATED)

    def test_login_requires_csrf_protection(self):
        self.signup("gallery-csrf-login")
        client = APIClient(enforce_csrf_checks=True)
        payload = {"username": "gallery-csrf-login", "password": "StrongPass123"}
        denied = client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        bootstrap = client.get("/api/auth/csrf/")
        allowed = client.post(
            "/api/auth/login/",
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=bootstrap.data["csrfToken"],
        )
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_invalid_or_expired_cookie_does_not_block_public_reads(self):
        client = APIClient()
        client.cookies["gallery_session"] = "invalid-stale-session"
        response = client.get("/api/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_cookie_is_treated_as_anonymous_for_public_reads(self):
        signup = self.signup("gallery-expired-public")
        gallery = Gallary.objects.get(username="gallery-expired-public")
        gallery.api_token_expires_at = timezone.now() - timedelta(seconds=1)
        gallery.save(update_fields=["api_token_expires_at"])
        client = APIClient()
        client.cookies["gallery_session"] = signup.cookies["gallery_session"].value
        response = client.get("/api/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        denied = client.post("/api/items/", {"title": "Must not create"}, format="json")
        self.assertIn(denied.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_signup_uses_configured_session_lifetime(self):
        from django.test import override_settings
        client = APIClient()
        with override_settings(GALLERY_SESSION_TTL_DAYS=2):
            response = client.post("/api/gallaries/", {
                "username": "gallery-signup-ttl",
                "password": "StrongPass123",
                "name": "Signup TTL Gallery",
                "email": "signup-ttl@example.com",
            }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(int(response.cookies["gallery_session"]["max-age"]), 2 * 86400)
        gallery = Gallary.objects.get(username="gallery-signup-ttl")
        self.assertAlmostEqual(
            (gallery.api_token_expires_at - timezone.now()).total_seconds(),
            2 * 86400,
            delta=5,
        )

    def test_public_gallery_directory_is_not_limited_by_signup_throttle(self):
        from django.test import override_settings
        with override_settings(GALLERY_SIGNUP_RATE="1/hour"):
            first = self.client.get("/api/gallaries/")
            second = self.client.get("/api/gallaries/")
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)

    def test_legacy_credential_migration_hashes_passwords_and_tokens(self):
        migration = import_module("artgallery.migrations.0005_hash_legacy_credentials")
        legacy = SimpleNamespace(
            password="LegacyPassword123",
            api_token="legacy-raw-token",
            save=Mock(),
        )
        existing_password_hash = make_password("AlreadyHashed123")
        already_hashed = SimpleNamespace(
            password=existing_password_hash,
            api_token="a" * 64,
            save=Mock(),
        )

        class GalleryManager:
            def all(self):
                return self

            def iterator(self):
                return iter((legacy, already_hashed))

        class HistoricalApps:
            def get_model(self, app_label, model_name):
                self.assert_model = (app_label, model_name)
                return SimpleNamespace(objects=GalleryManager())

        migration.hash_legacy_credentials(HistoricalApps(), None)

        self.assertTrue(check_password("LegacyPassword123", legacy.password))
        self.assertEqual(
            legacy.api_token,
            hashlib.sha256(b"legacy-raw-token").hexdigest(),
        )
        self.assertEqual(already_hashed.password, existing_password_hash)
        self.assertEqual(already_hashed.api_token, "a" * 64)
        legacy.save.assert_called_once_with(update_fields=["password", "api_token"])

    def test_existing_session_expiry_migration_sets_fourteen_day_expiry(self):
        migration = import_module("artgallery.migrations.0006_gallery_token_expiry")
        update = Mock()

        class GalleryManager:
            def filter(self, **kwargs):
                self.filter_kwargs = kwargs
                return self

            def update(self, **kwargs):
                update(**kwargs)

        class HistoricalApps:
            def get_model(self, app_label, model_name):
                return SimpleNamespace(objects=GalleryManager())

        started_at = timezone.now()
        migration.expire_existing_tokens(HistoricalApps(), None)
        expiry = update.call_args.kwargs["api_token_expires_at"]
        self.assertAlmostEqual(
            (expiry - started_at).total_seconds(),
            14 * 86400,
            delta=5,
        )

    def test_gallery_cannot_modify_another_gallery_profile(self):
        first = self.signup("gallery-profile-owner")
        self.signup("gallery-profile-other")
        response = self.client.patch(
            f"/api/gallaries/{first.data['gallery']['id']}/",
            {"name": "Unauthorized change"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_target_file_creation_assigns_owner_and_blocks_other_gallery(self):
        first = self.signup("gallery-target-owner")
        upload = SimpleUploadedFile(
            "target.bin",
            b"target-file-content",
            content_type="application/octet-stream",
        )
        created = self.client.post(
            "/api/targetfiles/",
            {"file": upload},
            format="multipart",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["gallary_id"], first.data["gallery"]["id"])

        self.signup("gallery-target-other")
        denied = self.client.delete(
            f"/api/targetfiles/{created.data['id']}/"
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
