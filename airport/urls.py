from rest_framework.routers import DefaultRouter
from .views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
    TicketViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register(r"airports", AirportViewSet, basename="airport")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register(r"airplanes", AirplaneViewSet, basename="airplane")
router.register(r"crew", CrewViewSet, basename="crew")
router.register(r"flights", FlightViewSet, basename="flight")
router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = router.urls
