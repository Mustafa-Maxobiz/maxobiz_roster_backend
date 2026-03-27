from rest_framework import viewsets, status
from positions.models.designation import Designation
from positions.serializers.designation import DesignationSerializer
from common.responses import APIResponse
from common.errors import raise_validation_error
from rest_framework.exceptions import ValidationError
from common.pagination import StandardResultsSetPagination


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    pagination_class = StandardResultsSetPagination

    # CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return APIResponse(
                success=True,
                message="Designation created successfully.",
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            raise_validation_error(e.detail)

    # UPDATE / PARTIAL_UPDATE
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return APIResponse(
                success=True,
                message="Designation updated successfully.",
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            raise_validation_error(e.detail)

    # RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            success=True,
            message="Designation fetched successfully.",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    # DESTROY
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse(
            success=True,
            message="Designation deleted successfully.",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )