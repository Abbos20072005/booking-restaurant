from django.db import models
from authentication.models import User
from .utils import name_validator, validate_uzb_number


class RestaurantCategory(models.Model):
    name = models.CharField(max_length=100,
                            validators=[name_validator], unique=True)  # pan-asian, europe, usa, arabic, turkish, family

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RestaurantImages(models.Model):
    images = models.ImageField(upload_to='images/restaurant')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.images


class Restaurant(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    service_fee = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)

    booking_count_total = models.IntegerField(default=0)
    booking_count_day_by_day = models.IntegerField(default=0)

    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=13, validators=[validate_uzb_number])
    email = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=2000, blank=True, null=True)
    longitude = models.CharField(max_length=2000, blank=True, null=True)

    category = models.ForeignKey(RestaurantCategory, on_delete=models.CASCADE)
    picture = models.ForeignKey(RestaurantImages, on_delete=models.CASCADE,
                                default='images/restaurant/default_restaurant.jpg')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=100, validators=[name_validator], unique=True)  # luxe, family, primary,

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RoomImages(models.Model):
    images = models.ImageField(upload_to='images/room')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.images


class RestaurantRoom(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[name_validator], unique=True)
    description = models.TextField(blank=True, null=True)
    pictures = models.ForeignKey(RoomImages, on_delete=models.CASCADE, default='images/room/default_room.jpg')

    people_number = models.IntegerField(default=0)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MenuType(models.Model):
    name = models.CharField(max_length=100, validators=[name_validator], unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RestaurantMenu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_type = models.ForeignKey(MenuType, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, validators=[name_validator], unique=True)
    description = models.TextField(blank=True, null=True)
    pictures = models.ImageField(upload_to='images/menu',
                                 default='images/menu/default_menu.jpg')
    ingredients = models.TextField(max_length=2000, blank=True, null=True)
    price = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu = models.ForeignKey(RestaurantMenu, on_delete=models.CASCADE, blank=True)
    comment = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    rating = models.IntegerField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.restaurant.name


class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rate = models.FloatField(default=0.0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.restaurant.name
