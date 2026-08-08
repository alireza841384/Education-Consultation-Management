from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet, SlotViewSet

app_name = "Appointment"

router = DefaultRouter()
router.register("schedules", ScheduleViewSet, basename="schedule")
router.register("appointment-slots", SlotViewSet, basename="appointment-slot")

urlpatterns = router.urls
