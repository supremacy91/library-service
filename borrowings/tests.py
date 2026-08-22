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


class BorrowingCreateTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpass123",
        )

        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee="1.50",
        )

        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-09-01",
        }

        response = self.client.post(
            reverse("borrowings:borrowing-list"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        borrowing = Borrowing.objects.get()

        self.assertEqual(
            borrowing.user,
            self.user,
        )
        self.assertEqual(
            borrowing.book,
            self.book,
        )

    def test_book_inventory_decreases_on_borrowing_creation(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-09-01",
        }

        self.client.post(
            reverse("borrowings:borrowing-list"),
            payload,
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.inventory,
            4,
        )

    def test_cannot_borrow_book_with_zero_inventory(self):
        self.book.inventory = 0
        self.book.save()

        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-09-01",
        }

        response = self.client.post(
            reverse("borrowings:borrowing-list"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Borrowing.objects.count(),
            0,
        )

    def test_unauthenticated_user_cannot_create_borrowing(self):
        self.client.force_authenticate(user=None)

        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-09-01",
        }

        response = self.client.post(
            reverse("borrowings:borrowing-list"),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
