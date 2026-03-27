from rest_framework import serializers
from positions.models.designation import Designation

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = "__all__"