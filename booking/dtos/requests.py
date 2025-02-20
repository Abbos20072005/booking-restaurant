from rest_framework import serializers

from booking.models import Booking, Occasion, OrderItems
from booking.serializers import OrderItemsSerializer


# INFO: This serializers used on views
class OrderItemsRequestSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = ['menu', 'amount', 'total_price']

    def get_total_price(self, obj):
        return obj.calculate_total_price()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        menu = instance.menu


class BookingRequestSerializer(serializers.ModelSerializer):
    # order_items = OrderItemsSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['author', 'room', 'number_of_people', 'client_number', 'client_name', 'planed_from',
                  'planed_to', "occasion", "status"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        order_items = instance.order_items.all()
        data['order_items'] = OrderItemsSerializer(order_items, many=True).data
        return data

    # def save(self, **kwargs):
    #     request = self.context['request']
    #     # request tookendan oladi shuning uchun token qoshilmasa {"author":["This field is required."]}
    #     user = User.objects.filter(user_id=request.user.id).first()
    #     self.validated_data['author'] = user
    #     return super().save(**kwargs)


class OccasionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occasion
        fields = ['name', ]


class PayingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking

    fields = ['author', "restaurants", 'client_name', "total_sum"]
