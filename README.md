# Library Service API

Library Service is a REST API for managing books, library users, and book borrowings.

The project was created as practice for a technical assessment. It replaces manual library workflows with an API-based system for managing book inventory, customers, and borrowings.

The project does not include a frontend. All functionality can be tested through the Django REST Framework Browsable API or Swagger UI.

## Features

Implemented functionality:

* Books CRUD
* Books permissions
* Custom user model with email authentication
* JWT authentication
* Custom `Authorize` authentication header
* User registration and profile management
* Borrowing list and detail endpoints
* Borrowing creation
* Automatic book inventory decrease when a book is borrowed
* Borrowing filtering by user and active status
* Swagger / OpenAPI documentation
* Automated API tests

## Tech Stack

* Python
* Django
* Django REST Framework
* Simple JWT
* drf-spectacular
* SQLite
* Git / GitHub

## Installation

Clone the repository:

```bash
git clone https://github.com/supremacy91/library-service.git
cd library-service
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/doc/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

## Authentication

The project uses JWT authentication.

Unlike the default SimpleJWT configuration, this project uses the custom HTTP header:

```text
Authorize: Bearer <access_token>
```

instead of:

```text
Authorization: Bearer <access_token>
```

### Register a user

```http
POST /api/users/
```

Example request:

```json
{
  "email": "user@test.com",
  "password": "StrongPass123!",
  "first_name": "John",
  "last_name": "Smith"
}
```

Example response:

```json
{
  "id": 1,
  "email": "user@test.com",
  "first_name": "John",
  "last_name": "Smith",
  "is_staff": false
}
```

The password is write-only and is never returned by the API.

### Obtain JWT tokens

```http
POST /api/users/token/
```

Request:

```json
{
  "email": "user@test.com",
  "password": "StrongPass123!"
}
```

Response:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

Use the access token for authenticated requests:

```text
Authorize: Bearer <access_token>
```

### Refresh access token

```http
POST /api/users/token/refresh/
```

Request:

```json
{
  "refresh": "<refresh_token>"
}
```

### User profile

Get the current user's profile:

```http
GET /api/users/me/
```

Update the profile:

```http
PUT /api/users/me/
PATCH /api/users/me/
```

Authentication is required.

## Books API

### List books

```http
GET /api/books/
```

Available to all users, including unauthenticated users.

### Get book details

```http
GET /api/books/<id>/
```

### Create a book

```http
POST /api/books/
```

Example:

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "HARD",
  "inventory": 5,
  "daily_fee": "1.50"
}
```

Possible cover values:

```text
HARD
SOFT
```

Only staff users can create books.

### Update a book

```http
PUT /api/books/<id>/
PATCH /api/books/<id>/
```

Only staff users can update books.

### Delete a book

```http
DELETE /api/books/<id>/
```

Only staff users can delete books.

## Borrowings API

All borrowing endpoints require authentication.

### List borrowings

```http
GET /api/borrowings/
```

Regular users can see only their own borrowings.

Staff users can see borrowings of all users.

The response contains detailed book information.

### Borrowing details

```http
GET /api/borrowings/<id>/
```

### Create a borrowing

```http
POST /api/borrowings/
```

Example:

```json
{
  "book": 1,
  "expected_return_date": "2026-09-01"
}
```

The authenticated user is automatically attached to the borrowing.

When a borrowing is created:

1. The API checks that the selected book has available inventory.
2. If `inventory == 0`, borrowing creation is rejected.
3. If the book is available, its inventory is decreased by `1`.
4. The current authenticated user is attached to the borrowing.

## Borrowing Filters

### Filter by active status

Active borrowing means that the book has not yet been returned:

```text
actual_return_date = null
```

Get active borrowings:

```http
GET /api/borrowings/?is_active=true
```

Get returned borrowings:

```http
GET /api/borrowings/?is_active=false
```

### Filter by user

Staff users can filter borrowings by user ID:

```http
GET /api/borrowings/?user_id=2
```

If a staff user does not provide `user_id`, borrowings for all users are returned.

Regular users always see only their own borrowings.

Filters can also be combined:

```http
GET /api/borrowings/?user_id=2&is_active=true
```

## Permissions

Books:

| Action      | Unauthenticated | Authenticated User | Staff |
| ----------- | --------------- | ------------------ | ----- |
| List books  | Yes             | Yes                | Yes   |
| View book   | Yes             | Yes                | Yes   |
| Create book | No              | No                 | Yes   |
| Update book | No              | No                 | Yes   |
| Delete book | No              | No                 | Yes   |

Borrowings:

| Action                | Unauthenticated | Authenticated User | Staff          |
| --------------------- | --------------- | ------------------ | -------------- |
| List borrowings       | No              | Own borrowings     | All borrowings |
| View borrowing        | No              | Yes                | Yes            |
| Create borrowing      | No              | Yes                | Yes            |
| Filter by `is_active` | No              | Own borrowings     | All borrowings |
| Filter by `user_id`   | No              | No                 | Yes            |

## Creating an Admin User

Create a superuser:

```bash
python manage.py createsuperuser
```

The project uses email instead of username for authentication.

Example:

```text
Email: admin@example.com
Password: ********
```

## Running Tests

Run all tests:

```bash
python manage.py test
```

Run tests for a specific application:

```bash
python manage.py test books
```

```bash
python manage.py test users
```

```bash
python manage.py test borrowings
```

The current test suite covers books, permissions, users, JWT authentication, borrowings creation, inventory management, and borrowing filtering.

## Django System Check

Run:

```bash
python manage.py check
```

## Swagger Authentication

Open:

```text
http://127.0.0.1:8000/api/doc/
```

Obtain an access token using:

```http
POST /api/users/token/
```

Click **Authorize** in Swagger and enter:

```text
Bearer <access_token>
```

After authorization, protected endpoints can be tested directly from Swagger.

## Implemented Flex Student Tasks

The following Coding tasks were selected and implemented:

1. Books Service CRUD
2. Books Service permissions
3. Users Service with email authentication and JWT
4. Borrowing List & Detail endpoints
5. Create Borrowing endpoint
6. Borrowings List filtering

## Project Structure

```text
library-service/
├── books/
├── borrowings/
├── users/
├── library_service/
├── manage.py
├── requirements.txt
├── schema.yml
└── README.md
```

## Author

GitHub:

```text
https://github.com/supremacy91
```
