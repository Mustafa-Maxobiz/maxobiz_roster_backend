from rest_framework import serializers
from positions.models.level import Level

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"