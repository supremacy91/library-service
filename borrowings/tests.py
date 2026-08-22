from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpass123",
        )

        self.other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="testpass123",
        )

        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee="1.50",
        )

        self.borrowing = Borrowing.objects.create(
            borrow_date=date.today(),
            expected_return_date=date(2026, 9, 1),
            book=self.book,
            user=self.user,
        )

    def test_unauthenticated_user_cannot_list_borrowings(self):
        response = self.client.get(
            reverse("borrowings:borrowing-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_list_borrowings(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("borrowings:borrowing-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_user_cannot_retrieve_borrowing(self):
        response = self.client.get(
            reverse(
                "borrowings:borrowing-detail",
                args=[self.borrowing.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_retrieve_borrowing(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse(
                "borrowings:borrowing-detail",
                args=[self.borrowing.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            self.borrowing.id,
        )
