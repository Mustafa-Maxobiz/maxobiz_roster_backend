# org_structure/views/organization.py
from rest_framework import viewsets, status
from org_structure.models.organization import Organization
from org_structure.serializers.organization import OrganizationSerializer
from common.responses import APIResponse
from common.pagination import StandardResultsSetPagination
from common.errors import raise_validation_error
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.filter(is_deleted=False).select_related('group')
    serializer_class = OrganizationSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise_validation_error(serializer.errors)
        self.perform_create(serializer)
        return APIResponse(
            success=True,
            message="Organization created successfully",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            raise_validation_error(serializer.errors)
        self.perform_update(serializer)
        return APIResponse(
            success=True,
            message="Organization updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return APIResponse(
            success=True,
            message="Organization deleted successfully",
            status=status.HTTP_204_NO_CONTENT
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            success=True,
            message="Organization details fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )
