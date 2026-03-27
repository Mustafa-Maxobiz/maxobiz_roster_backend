from rest_framework import serializers
from org_structure.models.organization import Organization
from org_structure.models.group import Group
from .group import GroupSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    # Read
    group = GroupSerializer(read_only=True)

    # Write
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.filter(is_deleted=False),
        source='group',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'group', 'group_id', 'is_deleted']
        read_only_fields = ['id', 'is_deleted']