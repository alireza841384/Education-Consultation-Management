
"""
    
# =====================================================
# Schedule
# =====================================================

GET     /api/schedules/
POST    /api/schedules/

GET     /api/schedules/{schedule_id}/
PATCH   /api/schedules/{schedule_id}/
DELETE  /api/schedules/{schedule_id}/


# =====================================================
# Schedule Actions
# =====================================================

# Generate slots from one or more time ranges
POST    /api/schedules/{schedule_id}/generate-slots/

# Preview generated slots (does not save)
POST    /api/schedules/{schedule_id}/preview-slots/

# Copy today's slots to other dates
POST    /api/schedules/{schedule_id}/copy-slots/

# Delete slots belonging to this schedule
POST    /api/schedules/{schedule_id}/clear-slots/


# =====================================================
# Appointment Slots
# =====================================================

GET     /api/appointment-slots/
POST    /api/appointment-slots/

GET     /api/appointment-slots/{slot_id}/
PATCH   /api/appointment-slots/{slot_id}/
DELETE  /api/appointment-slots/{slot_id}/


# =====================================================
# Bulk Slot Operations
# =====================================================

# Change status of multiple slots
PATCH   /api/appointment-slots/bulk-status/

# Delete multiple slots
POST    /api/appointment-slots/bulk-delete/


# =====================================================
# Appointments
# =====================================================

GET     /api/appointments/
POST    /api/appointments/

GET     /api/appointments/{appointment_id}/
PATCH   /api/appointments/{appointment_id}/
DELETE  /api/appointments/{appointment_id}/

"""

from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet

router = DefaultRouter()
router.register(
    "schedules",
    ScheduleViewSet,
    basename="schedule",
)

urlpatterns = router.urls
