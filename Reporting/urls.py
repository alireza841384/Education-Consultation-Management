from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Reporting.views import ReportingViewSet

router = DefaultRouter()
router.register("reports", ReportingViewSet, basename='report')

urlpatterns = [
    path("", include(router.urls)),
]
