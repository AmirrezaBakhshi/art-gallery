from rest_framework.test import APITestCase
from rest_framework import status

from .models import Gallary


class GalleryAuthenticationTests(APITestCase):
    def signup(self, username):
        return self.client.post("/api/gallaries/", {
            "username": username,
            "password": "StrongPass123",
            "name": f"{username} Gallery",
            "email": f"{username}@example.com",
        }, format="json")

    def test_signup_hashes_password_and_never_returns_it(self):
        response = self.signup("gallery-one")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertNotIn("password", response.data["gallery"])
        gallery = Gallary.objects.get(username="gallery-one")
        self.assertNotEqual(gallery.password, "StrongPass123")

    def test_login_returns_bearer_token_for_valid_credentials(self):
        self.signup("gallery-two")
        response = self.client.post("/api/auth/login/", {
            "username": "gallery-two",
            "password": "StrongPass123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["token"])

    def test_invalid_login_is_rejected(self):
        self.signup("gallery-three")
        response = self.client.post("/api/auth/login/", {
            "username": "gallery-three",
            "password": "incorrect",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_item_creation_requires_authentication_and_uses_authenticated_owner(self):
        response = self.client.post("/api/items/", {"title": "Public artwork"}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        signup = self.signup("gallery-four")
        token = signup.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
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
        second = self.signup("gallery-seven")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {first.data['token']}")
        created = self.client.post("/api/items/", {"title": "First gallery item"}, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {second.data['token']}")
        response = self.client.patch(
            f"/api/items/{created.data['id']}/",
            {"title": "Hijacked title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_revokes_the_current_token(self):
        signup = self.signup("gallery-logout")
        old_token = signup.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_token}")
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_token}")
        denied = self.client.post("/api/items/", {"title": "Should fail"}, format="json")
        self.assertIn(denied.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_legacy_plaintext_password_is_upgraded_after_login(self):
        gallery = Gallary.objects.create(
            username="legacy-gallery",
            password="LegacyPass123",
            name="Legacy Gallery",
            email="legacy@example.com",
        )
        response = self.client.post("/api/auth/login/", {
            "username": "legacy-gallery",
            "password": "LegacyPass123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gallery.refresh_from_db()
        self.assertNotEqual(gallery.password, "LegacyPass123")

