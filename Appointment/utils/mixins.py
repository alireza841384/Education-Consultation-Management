from django.db import transaction
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

class BulkDeleteSlotMixin:
    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self , request , *args , **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail" :
                             "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(id__in=ids)

        if queryset.count() != len(ids):
            raise serializers.ValidationError("Some slots were not found or you don't have permission to delete them.")
        
        if queryset.exclude(schedule__status='DRAFT').exists():
            raise serializers.ValidationError("Only slots of DRAFT schedules can be deleted.")

        with transaction.atomic():
                queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)