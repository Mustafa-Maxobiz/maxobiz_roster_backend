# serializer
from rest_framework import serializers
from org_structure.models.department import Department
from .organization import OrganizationSerializer
from .group import GroupSerializer
from org_structure.models.group import Group
from org_structure.models.organization import Organization


class DepartmentSerializer(serializers.ModelSerializer):
    # Read (nested)
    organizations = OrganizationSerializer(many=True, read_only=True)
    group = GroupSerializer(read_only=True)

    # Write
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.filter(is_deleted=False),
        source='group',
        write_only=True,
        required=False,
        allow_null=True
    )

    organization_ids = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_deleted=False),
        many=True,
        source='organizations',
        write_only=True,
        required=False
    )

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'description',
            'organizations',
            'organization_ids',
            'group',
            'group_id',
            'is_deleted'
        ]
        read_only_fields = ['id', 'is_deleted']