from rest_framework import serializers
from org_structure.models.group import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'is_deleted']
        read_only_fields = ['id', 'is_deleted']