from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet, SlotViewSet

app_name='Appointment'

router=DefaultRouter()
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns=[
    path('', include(router.urls)),

    path(
        'schedules/<int:schedule_pk>/slots/',
        SlotViewSet.as_view({
            'get':'list',
            'post':'create',
        }),
        name='slot-list-create',
    ),

    path(
        'schedules/<int:schedule_pk>/slots/<int:pk>/',
        SlotViewSet.as_view({
            'delete':'destroy',
        }),
        name='slot-delete',
    ),

    path(
        'schedules/<int:schedule_pk>/slots/bulk-delete/',
        SlotViewSet.as_view({
            'post':'bulk_delete',
        }),
        name='slot-bulk-delete',
    ),
]
