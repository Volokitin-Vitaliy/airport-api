from datetime import datetime, timezone as dt_timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
    Ticket,
)
from airport.serializers import TicketCreateSerializer


class AirportModelTests(TestCase):
    def setUp(self) -> None:
        self.airport_kyiv = Airport.objects.create(
            name="Kyiv International",
            closest_big_city="Kyiv"
        )
        self.airport_lviv = Airport.objects.create(
            name="Lviv",
            closest_big_city="Lviv"
        )
        self.route = Route.objects.create(
            source=self.airport_kyiv,
            destination=self.airport_lviv,
            distance=468,
        )
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="UR-PSB",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )
        self.crew_member = Crew.objects.create(
            first_name="Andrii",
            last_name="Shevchenko"
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2025, 1, 1, 12, 0, tzinfo=dt_timezone.utc),
        )
        self.flight.crew.set([self.crew_member])
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="strong-pass"
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )

    def test_airport_str(self) -> None:
        expected = "Kyiv International (Kyiv)"
        self.assertEqual(str(self.airport_kyiv), expected)

    def test_route_str(self) -> None:
        expected = f"{self.airport_kyiv} → {self.airport_lviv}"
        self.assertEqual(str(self.route), expected)

    def test_airplane_type_str(self) -> None:
        self.assertEqual(str(self.airplane_type), "Boeing 737")

    def test_airplane_capacity(self) -> None:
        self.assertEqual(self.airplane.capacity, 25 * 6)

    def test_airplane_str(self) -> None:
        expected = f"UR-PSB ({self.airplane_type})"
        self.assertEqual(str(self.airplane), expected)

    def test_crew_str(self) -> None:
        self.assertEqual(str(self.crew_member), "Andrii Shevchenko")

    def test_flight_str(self) -> None:
        expected_time = self.flight.departure_time.strftime("%Y-%m-%d %H:%M")
        expected = f"{self.route} | {expected_time}"
        self.assertEqual(str(self.flight), expected)

    def test_order_str(self) -> None:
        created_date = self.order.created_at.strftime("%Y-%m-%d")
        expected = f"Order #{self.order.id} by {self.user.email} on {created_date}"
        self.assertEqual(str(self.order), expected)

    def test_ticket_str(self) -> None:
        expected = f"Ticket 1-1 on flight {self.flight.id}"
        self.assertEqual(str(self.ticket), expected)


class TicketSerializerTests(TestCase):
    def setUp(self) -> None:
        airport_a = Airport.objects.create(name="A", closest_big_city="A")
        airport_b = Airport.objects.create(name="B", closest_big_city="B")
        route = Route.objects.create(source=airport_a, destination=airport_b, distance=100)
        airplane_type = AirplaneType.objects.create(name="TestType")
        airplane = Airplane.objects.create(
            name="T1",
            rows=2,
            seats_in_row=2,
            airplane_type=airplane_type
        )
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2025, 1, 1, 11, 0, tzinfo=dt_timezone.utc),
        )
        user = get_user_model().objects.create_user(
            email="duplicate@example.com",
            password="dup-pass"
        )
        self.order = Order.objects.create(user=user)
        Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order)

    def test_duplicate_seat_validation(self) -> None:
        data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order.id,
        }
        serializer = TicketCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        error_msg = serializer.errors["non_field_errors"][0]
        msg = str(error_msg).lower()
        self.assertTrue(
            "already" in msg or "unique" in msg,
            f"Unexpected error message: {error_msg}",
        )

    def test_unique_seat_allows_creation(self) -> None:
        data = {
            "row": 1,
            "seat": 2,
            "flight": self.flight.id,
            "order": self.order.id,
        }
        serializer = TicketCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        ticket = serializer.save()
        self.assertEqual(ticket.row, 1)
        self.assertEqual(ticket.seat, 2)
        self.assertEqual(ticket.flight, self.flight)
        self.assertEqual(ticket.order, self.order)


class FlightViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.airport_kyiv = Airport.objects.create(name="Kyiv", closest_big_city="Kyiv")
        self.airport_odessa = Airport.objects.create(name="Odesa", closest_big_city="Odesa")
        self.airport_lviv = Airport.objects.create(name="Lviv", closest_big_city="Lviv")

        self.route_kyiv_lviv = Route.objects.create(
            source=self.airport_kyiv,
            destination=self.airport_lviv,
            distance=468
        )
        self.route_odessa_kyiv = Route.objects.create(
            source=self.airport_odessa,
            destination=self.airport_kyiv,
            distance=500
        )
        airplane_type = AirplaneType.objects.create(name="TestPlane")
        airplane = Airplane.objects.create(
            name="PlaneA",
            rows=5,
            seats_in_row=4,
            airplane_type=airplane_type,
        )
        self.flight1 = Flight.objects.create(
            route=self.route_kyiv_lviv,
            airplane=airplane,
            departure_time=datetime(2025, 1, 1, 8, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
        )
        self.flight2 = Flight.objects.create(
            route=self.route_odessa_kyiv,
            airplane=airplane,
            departure_time=datetime(2025, 1, 2, 8, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2025, 1, 2, 9, 0, tzinfo=dt_timezone.utc),
        )

    def test_filter_by_source(self) -> None:
        url = reverse("flight-list")
        response = self.client.get(url, {"source": "Kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flights = response.data
        self.assertTrue(len(flights) >= 1)
        for fl in flights:
            source_name = fl["route"]["source"]["name"]
            self.assertIn("kyiv", source_name.lower())

    def test_filter_by_destination(self) -> None:
        url = reverse("flight-list")
        response = self.client.get(url, {"destination": "Kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flights = response.data
        self.assertTrue(len(flights) >= 1)
        for fl in flights:
            dest_name = fl["route"]["destination"]["name"]
            self.assertIn("kyiv", dest_name.lower())


class TicketViewSetTests(APITestCase):
    def setUp(self) -> None:
        a1 = Airport.objects.create(name="A1", closest_big_city="A")
        a2 = Airport.objects.create(name="A2", closest_big_city="B")
        route = Route.objects.create(source=a1, destination=a2, distance=100)
        airplane_type = AirplaneType.objects.create(name="Type")
        airplane = Airplane.objects.create(
            name="Plane",
            rows=2,
            seats_in_row=2,
            airplane_type=airplane_type
        )
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=datetime(2025, 1, 10, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2025, 1, 10, 12, 0, tzinfo=dt_timezone.utc),
        )
        self.user1 = get_user_model().objects.create_user(email="user1@example.com", password="pass1")
        self.user2 = get_user_model().objects.create_user(email="user2@example.com", password="pass2")
        self.order1 = Order.objects.create(user=self.user1)
        self.order2 = Order.objects.create(user=self.user2)
        Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order1)
        Ticket.objects.create(row=1, seat=2, flight=self.flight, order=self.order2)

    def test_list_tickets_returns_only_authenticated_users_tickets(self) -> None:
        url = reverse("ticket-list")
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        ticket = response.data[0]
        self.assertEqual(ticket["order"]["user"], self.user1.email)

    def test_create_ticket_assigns_ticket_to_order(self) -> None:
        self.client.force_authenticate(user=self.user1)
        order_response = self.client.post(reverse("order-list"), {})
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        order_id = order_response.data["id"]
        before_count = Ticket.objects.count()
        response = self.client.post(
            reverse("ticket-list"),
            {
                "row": 2,
                "seat": 1,
                "flight": self.flight.id,
                "order": order_id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), before_count + 1)
        created_ticket = Ticket.objects.latest("id")
        self.assertEqual(created_ticket.row, 2)
        self.assertEqual(created_ticket.seat, 1)
        self.assertEqual(created_ticket.flight, self.flight)
        self.assertEqual(created_ticket.order.id, order_id)


class OrderViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email="orderuser@example.com", password="pass123")

    def test_create_order_sets_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("order-list"), {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data["id"]
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.user, self.user)

    def test_list_orders_returns_only_user_orders(self) -> None:
        another_user = get_user_model().objects.create_user(email="other@example.com", password="pass456")
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=another_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], order1.id)


class AirplaneTypeViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email="plane@example.com", password="pass")

    def test_create_airplane_type_not_allowed(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("airplane-type-list")
        response = self.client.post(url, {"name": "NewType"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
