from django.db import models
from django.db import models
from django.contrib.auth.models import User

# Body Profile
class BodyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    height = models.FloatField()   # cm
    weight = models.FloatField()   # kg
    goal = models.CharField(max_length=20)
    workout_days = models.IntegerField()

    def __str__(self):
        return self.user.username


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    old_price = models.FloatField(blank=True, null=True)
    rating = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Supplement(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    old_price = models.FloatField(blank=True, null=True)
    rating = models.IntegerField(default=5)
    image = models.ImageField(upload_to='supplements/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):

    ITEM_TYPE = (
        ('product', 'Product'),
        ('supplement', 'Supplement'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.ImageField(upload_to='items/')

    type = models.CharField(max_length=20, choices=ITEM_TYPE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




# Price Comparison
class PriceComparison(models.Model):
    supplement = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    website = models.CharField(max_length=100)
    price = models.FloatField()
    rating = models.FloatField()

    def __str__(self):
        return self.website


# Workout Videos
class WorkoutVideo(models.Model):
    muscle_group = models.CharField(max_length=50)
    level = models.CharField(max_length=20)
    video_url = models.URLField()

    def __str__(self):
        return self.muscle_group


# Diet Plan
class DietPlan(models.Model):
    profile = models.OneToOneField(BodyProfile, on_delete=models.CASCADE)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    meal_plan = models.TextField()

    def __str__(self):
        return self.profile.user.username


# Orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
#  Registration

class RegistrationProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)   # ✅ IMPORTANT

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

# Media contents
class MediaContent(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='media_content/')
    redirect_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# orders
class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

# Order items
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def subtotal(self):
        return self.price * self.quantity