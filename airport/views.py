from rest_framework import viewsets, permissions
from .models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Ticket, Order
from .serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightSerializer,
    TicketSerializer,
    TicketCreateSerializer,
    OrderSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AirplaneTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related("route", "airplane").prefetch_related(
        "crew"
    )
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        if source:
            queryset = queryset.filter(route__source__name__icontains=source)
        if destination:
            queryset = queryset.filter(route__destination__name__icontains=destination)
        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.select_related("flight", "order__user").filter(
            order__user=self.request.user
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return TicketCreateSerializer
        return TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.prefetch_related("tickets").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
