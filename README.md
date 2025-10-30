# Airport API

Airport API is a RESTful service for managing airports, routes, airplanes, crews, flights, tickets, and orders.
It supports JWT authentication and provides public endpoints for general data access.

- Features

- User registration and authentication via JWT

- Manage airports, routes, airplanes, and crews

- Create tickets and orders for authenticated users

- Role-based access: unauthenticated users can only read data
------

### Tech Stack:

Python 3.11+

Django 5.2

Django REST Framework (DRF)

PostgreSQL

Docker & Docker Compose

------
### Installation:

- git clone https://github.com/<your_username>/airport-api.git
- cd airport-api
- docker compose up --build -d
- docker compose exec airport python manage.py migrate
------
### Authentication:

This project uses JWT (JSON Web Token) authentication.
Authentication endpoints are available under /api/user/.

Method	Endpoint	Description:
- POST	/api/user/register/	Register a new user
- POST	/api/user/token/	Obtain JWT token
- POST	/api/user/token/refresh/	Refresh token
- POST	/api/user/token/verify/	Verify token
- GET	/api/user/me/	Get or update user profile
------
### Main Endpoints:
- Airports	/api/airports/	Public
- Routes	/api/routes/	Public
- Airplane Types	/api/airplane-types/	Public
- Airplanes	/api/airplanes/	Authenticated
- Crew	/api/crew/	Authenticated
- Flights	/api/flights/	Public read
- Tickets	/api/tickets/	Authenticated
- Orders	/api/orders/	Authenticated
------
### Admin Panel

Create a superuser to access the Django admin panel:

- docker compose exec airport python manage.py createsuperuser


Then go to:

http://127.0.0.1:8000/admin/