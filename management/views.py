from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date
from restaurants.models import Restaurant
from booking.models import Booking
from .models import Role, Manager, Employee, PerformanceReview, Project, Task, LeaveRequest
from .serializers import RestaurantSerializer, BookingSerializer, ManagerSerializer, EmployeeSerializer, \
    DateRangeQuerySerializer, DateQuerySerializer
from payment.models import PaymentWithHistory
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi


class RestaurantViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all restaurants",
        operation_summary="Get all restaurants",
        responses={
            200: openapi.Response(
                description='List of all restaurants',
            )
        },
    )
    def list(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Retrieve a restaurant detail",
        operation_summary="Get restaurant details",
        responses={
            200: openapi.Response(
                description='Restaurant detail',
            ),
            404: openapi.Response(
                description='Restaurant not found',
            )
        },
    )
    def retrieve(self, request, rest_id):
        exists = Restaurant.objects.filter(pk=rest_id)
        if not exists.exists():
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RestaurantSerializer(exists.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Show the balance of a restaurant",
        operation_summary="Retrieve restaurant balance",
        responses={
            200: openapi.Response(
                description="Restaurant balance",
            ),
            404: openapi.Response(
                description="Restaurant not found",
            ),
        },
    )
    def balance(self, request, rest_id):
        restaurant = Restaurant.objects.filter(pk=rest_id).first()
        balance = restaurant.balance
        return Response({f'total balance: {balance}'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get statistics of bookings based on date range",
        operation_summary="Get booking statistics based on date range",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date in YYYY-MM-DD format",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date in YYYY-MM-DD format",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Booking statistics',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_bookings': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_revenue': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
                    }
                )
            ),
            400: openapi.Response(
                description='Invalid date format or date range'
            )
        },
    )
    def statistics(self, request, rest_id):
        query_serializer = DateRangeQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        parsed_start_date = query_serializer.validated_data['start_date']
        parsed_end_date = query_serializer.validated_data['end_date']

        if parsed_start_date > parsed_end_date:
            return Response({'error': 'Start date cannot be after end date'}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(restaurants_id=rest_id,
                                          booked_time__date__range=[parsed_start_date, parsed_end_date])
        total_bookings = bookings.count()
        total_revenue = bookings.aggregate(total=Sum('total_sum'))['total'] or 0

        stats = {
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
        }
        return Response(stats, status=status.HTTP_200_OK)


class BookingViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="List bookings based on date",
        operation_summary="Get all bookings based on date",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Date in YYYY-MM-DD format",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='List of all bookings',
                schema=BookingSerializer(many=True)
            ),
            400: openapi.Response(
                description='"Date has wrong format. Use one of these formats instead: YYYY-MM-DD."'
            )
        },
    )
    def list(self, request, rest_id):
        query_serializer = DateQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        parsed_date = query_serializer.validated_data['date']
        bookings = Booking.objects.filter(restaurants_id=rest_id, booked_time__date=parsed_date)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Retrieve a booking detail",
        operation_summary="Get booking details",
        responses={
            200: openapi.Response(
                description='Booking detail',
            ),
            404: openapi.Response(
                description='Booking not found',
            ),
        },
    )
    def retrieve(self, request, rest_id, booking_id):
        booking_exists = Booking.objects.filter(pk=booking_id, restaurants_id=rest_id)
        if not booking_exists.exists():
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        bookings = booking_exists
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Cancel the booking",
        operation_summary="Cancel booking",
        responses={
            200: openapi.Response(
                description='Booking cancelled',
            ),
            404: openapi.Response(
                description='Booking not found',
            )
        },
    )
    def cancel(self, request, rest_id, booking_id):
        booking_exists = Booking.objects.filter(pk=booking_id, restaurant_id=rest_id).first()
        if booking_exists is None:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        booking_exists.status = False
        booking_exists.save(update_fields=['status'])
        return Response({'status': 'Booking cancelled'}, status=status.HTTP_200_OK)


class ManagementViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new manager for the restaurant",
        operation_summary="Add a manager",
        request_body=ManagerSerializer,
        responses={
            201: openapi.Response(
                description='Manager Added Successfully',
            ),
            400: openapi.Response(
                description='Invalid data',
            )
        },
    )
    def create(self, request, *args, **kwargs):
        manager_serializer = ManagerSerializer(data=request.data)
        if manager_serializer.is_valid():
            manager_serializer.save()
            return Response({"message": "Manager Added Successfully", "status": status.HTTP_201_CREATED})
        return Response({"message": "Invalid data", "status": status.HTTP_400_BAD_REQUEST})

    @swagger_auto_schema(
        operation_description="List all restaurant managers",
        operation_summary="Get all managers",
        responses={
            200: openapi.Response(
                description='List of all managers',
            )
        },
    )
    def list(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployerViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new employee",
        operation_summary="Add an employee",
        request_body=EmployeeSerializer,
        responses={
            201: openapi.Response(
                description='Employee added Successfully',
            ),
            400: openapi.Response(
                description='Invalid data',
            )
        },
    )
    def create(self, request, *args, **kwargs):
        employer_serializer = EmployeeSerializer(data=request.data)
        if employer_serializer.is_valid():
            employer_serializer.save()
            return Response({"message": "Employee Added Successfully", "status": status.HTTP_201_CREATED})
        return Response({"message": "Invalid data", "status": status.HTTP_400_BAD_REQUEST})

    @swagger_auto_schema(
        operation_description="List the employees of a manager",
        operation_summary="Get all employees",
        responses={
            200: openapi.Response(
                description='List of all employees',
            )
        },
    )
    def list(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
