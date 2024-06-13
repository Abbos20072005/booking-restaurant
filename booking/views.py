from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from restaurants.models import RestaurantMenu
from booking.models import Booking, Occasion, OrderFreeTable, OrderFreeTime, OrderItems
from booking.serializers import BookingSerializer, OccasionSerializer, OrderFreeTableSerializer, \
    OrderFreeTimeSerializer

class BookingViewSet(ViewSet):
    def create_booking(self, request, *args, **kwargs):
        booking_serializer = BookingSerializer(data=request.data)
        if booking_serializer.is_valid():
            booking_serializer.save()
            return Response({"message": "Booking Added Sucessfully", "status": status.HTTP_201_CREATED})
        return Response({"message": "please fill the datails", "status": status.HTTP_400_BAD_REQUEST})

    def show_bookings(self, request):
        queryset = Booking.objects.all()
        bookings = BookingSerializer(queryset, many=True).data
        return Response(data={'bookings': bookings}, status=status.HTTP_200_OK)


class BookingActionsViewSet(ViewSet):
    def detail_booking(self, request, pk):
        booking_detail = Booking.objects.filter(id=pk).first()
        booking_serializer = BookingSerializer(booking_detail).data
        return Response(data={'data': booking_serializer.data, 'message': f'{pk} id li buyurtma'},
                        status=status.HTTP_200_OK)

    def pay_booking(self, request, pk):
        booking_detail = Booking.objects.filter(id=pk).first()
        booking_pay = {}
        return Response(data={'data': booking_pay, 'message': f'{pk} id'}, )

    def cancel_booking(self, request, *args, **kwargs):
        pass

    def set_status(self, request, *args, **kwargs):
        pass

    def delete_booking(self, request, *args, **kwargs):
        booking_data = Booking.objects.filter(id=kwargs['pk'])
        if booking_data:
            booking_data.delete()
            return Response({"message": "Product delete Sucessfully", "status": status.HTTP_200_OK})
        return Response({"message": "Product data not found", "status": status.HTTP_400_BAD_REQUEST})


class OccasionViewSet(ViewSet):
    def create_occasion(self, request, *args, **kwargs):
        queryset = Occasion.objects.create(**request.data)
        queryset.save()
        return Response(data={'id': queryset.pk, 'message': 'your occasion has been created'}, )

    def list_occasions(self, request):
        queryset = Occasion.objects.all()
        occasions = OccasionSerializer(queryset, many=True).data
        return Response(data={'occasions': occasions}, )


class OccasionActionsViewSet(ViewSet):
    def edit_occasion(self, request, pk):
        occasion = Occasion.objects.filter(id=pk).first()
        if occasion:
            occasion.name = request.data['occasion_name']
            occasion.save(update_fields=['occasion_name'])
            return Response(data={"message": f"{occasion} data was changed"}, status=status.HTTP_200_OK)
        return Response(data={"message": "Your data doesn't found"}, status=status.HTTP_400_BAD_REQUEST)


class FreeOrderViewSet(ViewSet):

    def add_free_table(self, request):
        if request.method == "POST":
            obj = OrderFreeTable.objects.create(table_name=request.data['table_name'])
            obj.save()
            return Response(data={'message': 'Table successfully created'}, status=status.HTTP_201_CREATED)
        table = OrderFreeTable.objects.all()
        serializer_table = OrderFreeTableSerializer(table, many=True).data
        return Response(data={'message': serializer_table}, status=status.HTTP_200_OK)

    def ordered_times_view(self, request, pk):
        if request.method == 'POST':
            obj = OrderFreeTime.objects.create(table_id=pk, free_time=request.data['free_time'])
            obj.save()
            return Response(data={'message': 'You are successfully order table'}, status=status.HTTP_201_CREATED)
        time = OrderFreeTime.objects.all()
        serializer = OrderFreeTimeSerializer(time, many=True).data
        return Response(data={'message': serializer}, status=status.HTTP_200_OK)
