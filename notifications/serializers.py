from rest_framework import serializers
from notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ['user']
        read_only_fields = ('id', )


    def create(self, validated_data):
        request = self.context.get('request')
        Notification.objects.create(**validated_data, user=request.user)
        return Notification