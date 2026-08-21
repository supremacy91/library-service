from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book


class BookApiTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("1.50"),
        )

    def test_list_books(self):
        response = self.client.get(reverse("book-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Clean Code")

    def test_retrieve_book(self):
        response = self.client.get(
            reverse("book-detail", args=[self.book.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Clean Code")
        self.assertEqual(response.data["author"], "Robert C. Martin")

    def test_create_book(self):
        payload = {
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "cover": Book.CoverType.SOFT,
            "inventory": 3,
            "daily_fee": "2.00",
        }

        response = self.client.post(
            reverse("book-list"),
            payload,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Book.objects.filter(
                title="The Pragmatic Programmer"
            ).exists()
        )

    def test_update_book(self):
        payload = {
            "title": "Clean Code Updated",
        }

        response = self.client.patch(
            reverse("book-detail", args=[self.book.id]),
            payload,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.title,
            "Clean Code Updated",
        )

    def test_delete_book(self):
        response = self.client.delete(
            reverse("book-detail", args=[self.book.id])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Book.objects.filter(id=self.book.id).exists()
        )
