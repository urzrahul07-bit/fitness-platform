from django.db import models

# Create your models here.
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


# Supplements
class Supplement(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField()

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
    

#product

class Product(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="products/")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rating = models.PositiveIntegerField(default=5)

    description = models.TextField(blank=True)   # ✅ NEW FIELD

    redirect_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    

class MediaContent(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='media_content/')
    redirect_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
