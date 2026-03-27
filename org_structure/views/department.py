# org_structure/views/department.py
from rest_framework import viewsets, status
from org_structure.models.department import Department
from org_structure.serializers.department import DepartmentSerializer
from common.responses import APIResponse
from common.pagination import StandardResultsSetPagination
from common.errors import raise_validation_error
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_deleted=False)\
                                 .select_related('group')\
                                 .prefetch_related('organizations')
    serializer_class = DepartmentSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise_validation_error(serializer.errors)
        self.perform_create(serializer)
        return APIResponse(
            success=True,
            message="Department created successfully",
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
            message="Department updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return APIResponse(
            success=True,
            message="Department deleted successfully",
            status=status.HTTP_204_NO_CONTENT
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            success=True,
            message="Department details fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )