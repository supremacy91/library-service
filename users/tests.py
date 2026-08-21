from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class UserApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Smith",
        )

    def test_create_user(self):
        payload = {
            "email": "newuser@test.com",
            "password": "StrongPass123!",
            "first_name": "Alice",
            "last_name": "Brown",
        }

        response = self.client.post(
            reverse("users:create"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(
            email="newuser@test.com"
        )

        self.assertTrue(
            user.check_password("StrongPass123!")
        )
        self.assertFalse(user.is_staff)

    def test_password_not_returned_in_response(self):
        payload = {
            "email": "newuser@test.com",
            "password": "StrongPass123!",
            "first_name": "Alice",
            "last_name": "Brown",
        }

        response = self.client.post(
            reverse("users:create"),
            payload,
        )

        self.assertNotIn("password", response.data)

    def test_user_cannot_make_themselves_staff(self):
        payload = {
            "email": "newuser@test.com",
            "password": "StrongPass123!",
            "is_staff": True,
        }

        response = self.client.post(
            reverse("users:create"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(
            email="newuser@test.com"
        )

        self.assertFalse(user.is_staff)

    def test_obtain_jwt_token(self):
        payload = {
            "email": "user@test.com",
            "password": "StrongPass123!",
        }

        response = self.client.post(
            reverse("users:token_obtain_pair"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_jwt_token(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("users:token_refresh"),
            {
                "refresh": str(refresh),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(
            reverse("users:me")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_access_me(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {access_token}"
        )

        response = self.client.get(
            reverse("users:me")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["email"],
            "user@test.com",
        )

    def test_authenticated_user_can_update_profile(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {access_token}"
        )

        response = self.client.patch(
            reverse("users:me"),
            {
                "first_name": "Updated",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Updated",
        )

    def test_authenticated_user_can_change_password(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {access_token}"
        )

        response = self.client.patch(
            reverse("users:me"),
            {
                "password": "NewStrongPass123!",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewStrongPass123!"
            )
        )