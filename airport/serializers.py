from rest_framework import serializers
from .models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Ticket, Order


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Route
        fields = "__all__"


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = "__all__"


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)

    class Meta:
        model = Flight
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = OrderSerializer()

    class Meta:
        model = Ticket
        fields = "__all__"


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["row", "seat", "flight", "order"]

    def validate(self, data):
        if Ticket.objects.filter(
            flight=data["flight"], row=data["row"], seat=data["seat"]
        ).exists():
            raise serializers.ValidationError("This place is already taken.")
        return data
