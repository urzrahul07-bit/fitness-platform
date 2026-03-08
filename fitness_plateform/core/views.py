from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import RegistrationProfile
from .models import Product
from django.shortcuts import redirect, render, get_object_or_404
from .models import MediaContent   # or your Product model

import razorpay
from django.conf import settings
from django.shortcuts import render


from .models import (
    BodyProfile,
    DietPlan,
    Supplement,
    WorkoutVideo,
    Order,
    RegistrationProfile
)


# Home Page
def home(request):
    return render(request, 'home.html')


def nav(request):
    return render(request, 'nav.html')

# BMI Calculation
def calculate_bmi(weight, height):
    height_m = height / 100
    return round(weight / (height_m * height_m), 2)


# BMR Calculation
def calculate_bmr(weight, height, age, gender):
    if gender == 'male':
        return 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        return 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)


# -------------------------------
# User Body Profile
# -------------------------------
@login_required
def profile(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        height = float(request.POST.get('height'))
        weight = float(request.POST.get('weight'))
        goal = request.POST.get('goal')
        workout_days = int(request.POST.get('workout_days'))

        BodyProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'age': age,
                'gender': gender,
                'height': height,
                'weight': weight,
                'goal': goal,
                'workout_days': workout_days
            }
        )

        return redirect('diet')

    body_profile = BodyProfile.objects.filter(user=request.user).first()

    return render(request, 'profile.html', {
        'body_profile': body_profile})
   


# -------------------------------
# Diet Plan
# -------------------------------
@login_required
def diet_plan(request):
    profile = BodyProfile.objects.filter(user=request.user).first()

    if not profile:
        return redirect('profile')

    bmi = calculate_bmi(profile.weight, profile.height)
    bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)

    activity_factor = 1.2 if profile.workout_days <= 2 else 1.5
    calories = int(bmr * activity_factor)

    if profile.goal == 'bulking':
        calories += 300
    elif profile.goal == 'cutting':
        calories -= 300

    protein = int(profile.weight * 2)
    carbs = int((calories * 0.5) / 4)
    fats = int((calories * 0.25) / 9)

    DietPlan.objects.update_or_create(
        profile=profile,
        defaults={
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats,
            'meal_plan': 'Breakfast, Lunch, Dinner as per calories'
        }
    )

    context = {
        'bmi': bmi,
        'calories': calories,
        'protein': protein,
        'carbs': carbs,
        'fats': fats
    }

    return render(request, 'diet.html', context)


# -------------------------------
# Register
# -------------------------------
def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        if User.objects.filter(username=username).exists():
            # return back to login page (popup will be there)
            return redirect("login")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        RegistrationProfile.objects.create(
            user=user,
            phone=phone
        )

        login(request, user)
        return redirect("dashboard")

    # 👇 IMPORTANT
    return redirect("login")
# -------------------------------
# Profile_update
# -------------------------------
@login_required
def profile_update(request):

    profile, created = RegistrationProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        profile.phone = request.POST.get("phone")
        profile.gender = request.POST.get("gender")
        profile.city = request.POST.get("city")

        dob = request.POST.get("date_of_birth")
        if dob:
            profile.date_of_birth = dob

        profile.save()

        return redirect("dashboard")

    return render(request, "profile_update.html", {
        "profile": profile
    })
# -------------------------------
# Login
# -------------------------------
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login details')

    return render(request, 'login.html')


# -------------------------------
# Logout
# -------------------------------
def user_logout(request):
    logout(request)
    return redirect('login')


# -------------------------------
# User Dashboard
# -------------------------------
@login_required
def user_dashboard(request):

    profile = BodyProfile.objects.filter(user=request.user).first()
    diet = None

    if profile:
        diet = DietPlan.objects.filter(profile=profile).first()

    context = {
        'profile': profile,
        'diet': diet,
        'supplement_count': Supplement.objects.count(),
        'video_count': WorkoutVideo.objects.count(),
        'order_count': Order.objects.filter(user=request.user).count()
    }

    return render(request, 'dashboard.html', context)


# -------------------------------
# Admin Dashboard
# -------------------------------
@staff_member_required
def admin_dashboard(request):

    context = {
        'total_users': User.objects.count(),
        'total_products': Supplement.objects.count(),
        'total_orders': Order.objects.count(),
        'total_videos': WorkoutVideo.objects.count()
    }

    return render(request, 'admin_dashboard.html', context)




def home(request):
    return render(request,'home.html')


def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})


# def add_to_cart(request, id):
#     product = get_object_or_404(MediaContent, id=id)

#     cart = request.session.get('cart', {})

#     if str(id) in cart:
#         cart[str(id)]['qty'] += 1
#     else:
#         cart[str(id)] = {
#             'title': product.name,
#             'price': float(0),   # change if you have price field
#             'image': product.image.url,
#             'qty': 1
#         }

    # request.session['cart'] = cart
    # return redirect(request.META.get('HTTP_REFERER','shop'))




# def add_to_cart(request, id):
#     product = get_object_or_404(Product, id=id)

#     cart = request.session.get('cart', {})

#     qty = int(request.GET.get('qty', 1))

#     if str(id) in cart:
#         cart[str(id)]['qty'] += qty
#     else:
#         cart[str(id)] = {
#             'name': product.name,
#             'price': float(product.price),
#             'image': product.image.url if product.image else '',
#             'qty': qty
#         }

#     request.session['cart'] = cart
#     return redirect(request.META.get('HTTP_REFERER', '/'))


# def update_cart(request, id):
#     cart = request.session.get('cart', {})

#     if str(id) in cart:
#         qty = int(request.GET.get('qty', 1))

#         if qty <= 0:
#             del cart[str(id)]
#         else:
#             cart[str(id)]['qty'] = qty

#     request.session['cart'] = cart
#     return redirect(request.META.get('HTTP_REFERER', '/'))


# # views.py

# def cart_page(request):

#     cart = request.session.get('cart', {})

#     cart_items = []
#     cart_total = 0

#     for key, item in cart.items():
#         qty = int(item['qty'])
#         price = float(item['price'])

#         subtotal = price * qty
#         cart_total += subtotal

#         cart_items.append({
#             'key': key,
#             'name': item['name'],
#             'price': price,
#             'qty': qty,
#             'image': item['image'],
#             'subtotal': subtotal
#         })

#     return render(request, "cart.html", {
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#     })





# def remove_from_cart(request, id):
#     cart = request.session.get('cart', {})

#     if str(id) in cart:
#         del cart[str(id)]

#     request.session['cart'] = cart
#     return redirect(request.META.get('HTTP_REFERER','shop'))



from django.shortcuts import render, redirect, get_object_or_404
from .models import Product   # your product model

# ---------------- ADD ----------------

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart = request.session.get('cart', {})

    pid = str(id)

    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url if product.image else '',
            'qty': 1
        }

    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ---------------- UPDATE QTY ----------------

def update_cart(request, key):
    cart = request.session.get('cart', {})

    qty = int(request.GET.get('qty', 1))

    if key in cart:
        cart[key]['qty'] = max(1, qty)

    request.session['cart'] = cart
    return redirect('cart')


# ---------------- REMOVE ----------------

def remove_from_cart(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]

    request.session['cart'] = cart
    return redirect('cart')


# ---------------- CART PAGE ----------------

def cart_page(request):

    cart = request.session.get('cart', {})

    cart_items = []
    cart_total = 0

    for key, item in cart.items():
        subtotal = item['price'] * item['qty']
        cart_total += subtotal

        cart_items.append({
            'key': key,
            'name': item['name'],
            'price': item['price'],
            'qty': item['qty'],
            'image': item['image'],
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    thumbnails = Product.objects.exclude(id=id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'thumbnails': thumbnails
    })

# def checkout(request):
#     cart = request.session.get("cart", {})

#     order_items = []
#     subtotal = 0

#     for key, item in cart.items():
#         line_total = float(item["price"]) * int(item["qty"])
#         subtotal += line_total

#         order_items.append({
#             "id": key,
#             "name": item["name"],
#             "qty": item["qty"],
#             "price": item["price"],
#             "line_total": line_total
#         })

#     context = {
#         "order_items": order_items,
#         "subtotal": subtotal,
#         "total": subtotal,   # for now same
#     }

#     return render(request, "checkout.html", context)

def checkout(request):

    cart = request.session.get('cart', {})
    total = 0

    for item in cart.values():
        total += float(item['price']) * int(item['qty'])

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total * 100),   # paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "cart": cart,
        "cart_total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"]
    }

    return render(request, "checkout.html", context)

def payment_success(request):

    # clear cart after payment
    if "cart" in request.session:
        del request.session["cart"]

    return render(request, "payment_success.html")