from rest_framework import serializers

from core.models import Todo


class TodoSerializer(serializers.ModelSerializer):
    """Serialize a todos"""

    class Meta:
        model = Todo
        fields = (
            'id', 'task', 'description',
        )
        read_only_fields = ('id',)

