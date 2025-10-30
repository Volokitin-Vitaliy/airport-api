from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserApiTests(APITestCase):
    def test_register_user_successfully(self) -> None:
        payload = {
            "email": "newuser@example.com",
            "password": "testpass123",
        }
        res = self.client.post(reverse("user:create"), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_register_user_email_exists(self) -> None:
        payload = {"email": "dup@example.com", "password": "pwd123"}
        create_user(**payload)
        res = self.client.post(reverse("user:create"), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def setUp(self) -> None:
        self.user_email = "tokenuser@example.com"
        self.user_password = "secret123"
        self.user = create_user(email=self.user_email, password=self.user_password)

    def test_create_token_for_user(self) -> None:
        payload = {"email": self.user_email, "password": self.user_password}
        res = self.client.post(reverse("user:token_obtain_pair"), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_create_token_invalid_credentials(self) -> None:
        payload = {"email": self.user_email, "password": "wrongpass"}
        res = self.client.post(reverse("user:token_obtain_pair"), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", res.data)
        self.assertNotIn("refresh", res.data)

    def test_retrieve_user_unauthenticated(self) -> None:
        res = self.client.get(reverse("user:manage"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_success(self) -> None:
        token_res = self.client.post(
            reverse("user:token_obtain_pair"),
            {"email": self.user_email, "password": self.user_password},
        )
        access_token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        res = self.client.get(reverse("user:manage"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user_email)
        self.assertNotIn("password", res.data)

    def test_update_user_profile(self) -> None:
        token_res = self.client.post(
            reverse("user:token_obtain_pair"),
            {"email": self.user_email, "password": self.user_password},
        )
        access_token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        new_email = "updated@example.com"
        new_password = "newsecret456"
        res = self.client.patch(
            reverse("user:manage"),
            {"email": new_email, "password": new_password},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)
        self.assertTrue(self.user.check_password(new_password))
