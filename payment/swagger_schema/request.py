from rest_framework import serializers
from payment.models import PaymentWithHistory


class PaymentSwagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentWithHistory
        fields = ['pan', 'expire_month', 'amount', 'booking_id']