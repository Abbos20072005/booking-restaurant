from rest_framework import serializers
from .models import Manager, Administrator
from authentication.models import User


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['user', 'phone_number', 'date_of_birth', 'hire_date']
        read_only_fields = ['user']

    def save(self, **kwargs):
        request = self.context['request']
        user = User.objects.filter(user_id=request.user.id).first()
        self.validated_data['user'] = user
        return super().save(**kwargs)


class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = ['user', 'phone_number', 'date_of_birth', 'hire_date']


class DateQuerySerializer(serializers.Serializer):
    date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'], required=True)


class DateRangeQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'], required=True)
    end_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'], required=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date")
        return data
