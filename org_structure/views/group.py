# org_structure/views/group.py
from rest_framework import viewsets, status
from org_structure.models.group import Group
from org_structure.serializers.group import GroupSerializer
from common.responses import APIResponse
from common.pagination import StandardResultsSetPagination
from common.errors import raise_validation_error
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.filter(is_deleted=False)
    serializer_class = GroupSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise_validation_error(serializer.errors)
        self.perform_create(serializer)
        return APIResponse(
            success=True,
            message="Group created successfully",
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
            message="Group updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return APIResponse(
            success=True,
            message="Group deleted successfully",
            status=status.HTTP_204_NO_CONTENT
        )