from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import RegistrationProfile
from django.conf import settings
from django.http import HttpResponse
from django.core.paginator import Paginator

from .models import MediaContent   # or your Product model
from .models import Order
from .models import Product, Item # your product model
from .models import Supplement # your SupplementDetails
from .models import (
    BodyProfile,
    DietPlan,
    Supplement,
    WorkoutVideo,
    Order,
    RegistrationProfile
)

from django.shortcuts import render
from reportlab.pdfgen import canvas
import razorpay




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


# ---------------- ADD ----------------

def add_to_cart(request, type, id):

    # Detect item type
    if type == "product":
        item = get_object_or_404(Product, id=id)
    else:
        item = get_object_or_404(Supplement, id=id)

    cart = request.session.get('cart', {})

    key = f"{type}-{id}"   # unique key
    image = item.image.url if item.image else ""

    if key in cart:
        cart[key]['qty'] += 1
    else:
        cart[key] = {
            'id': id,
            'type': type,
            'name': item.name,
            'price': float(item.price),
            'image': image,
            'qty': 1
        }

    request.session['cart'] = cart

    return redirect(request.META.get('HTTP_REFERER', '/'))


#----------------- BUY ----------------

def buy_now(request, type, id):

    if type == "product":
        item = get_object_or_404(Product,id=id)

    elif type == "supplement":
        item = get_object_or_404(Supplement,id=id)

    cart = {
        str(id):{
            'name': item.name,
            'price': float(item.price),
            'qty':1
        }
    }

    request.session['cart'] = cart

    return redirect('checkout')


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

# ---------------- CART PAGE ----------------

def cart_page(request):

    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for key, item in cart.items():

        subtotal = item['price'] * item['qty']
        total += subtotal

        cart_items.append({
            'key': key,
            'name': item['name'],
            'price': item['price'],
            'qty': item['qty'],
            'image': item.get('image',''),
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
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

# def checkout(request):

    cart = request.session.get('cart', {})
    order_items = []
    subtotal = 0

    for item in cart.values():
        line_total = float(item['price']) * int(item['qty'])
        subtotal += line_total

        order_items.append({
            "name": item['name'],
            "qty": item['qty'],
            "line_total": line_total
        })

    total = subtotal

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "order_items": order_items,
        "subtotal": subtotal,
        "total": total,
        "cart_total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"]
    }

    return render(request, "checkout.html", context)


def create_order_items(order, cart):

    for item in cart.values():
        OrderItem.objects.create(
            order=order,
            product_name=item["name"],
            price=item["price"],
            quantity=item["qty"]
        )


def checkout(request):

    cart = request.session.get("cart", {})
    total = 0

    for item in cart.values():
        total += float(item["price"]) * int(item["qty"])

    order = Order.objects.create(
        user=request.user,
        total=total
    )

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "order_id": order.id,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
    }

    return render(request, "checkout.html", context)

# def payment_success(request, order_id):

    order = Order.objects.get(id=order_id)

    return render(request,"payment_success.html",{
        "order_id":order.id
    })


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


def download_invoice(request, order_id):

    order = Order.objects.get(id=order_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    y = 800

    p.drawString(100, y, f"Invoice for Order #{order.id}")
    y -= 40

    p.drawString(100, y, f"Date: {order.created_at}")
    y -= 40

    p.drawString(100, y, "Items:")
    y -= 30

    for item in order.items.all():

        p.drawString(
            100,
            y,
            f"{item.product_name}  x{item.quantity}  ₹{item.price}"
        )

        y -= 20

    y -= 20

    p.drawString(100, y, f"Total: ₹{order.total}")

    p.save()

    return response

# Home Page
def home(request):
    return render(request, 'home.html')


def nav(request):
    return render(request, 'nav.html')


def orders(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request,"orders.html",{"orders":user_orders})


def order_history(request):

    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "order_history.html", {"orders": orders})       


def product_detail(request, type, id):

    if type == "product":
        item = get_object_or_404(Product, id=id)

    else:
        item = get_object_or_404(Supplement, id=id)

    context = {
        "item": item,
        "type": type
    }

    return render(request, "product_detail.html", context)


def payment_success(request, order_id):

    order = Order.objects.get(id=order_id)

    return render(request, "payment_success.html", {
        "order": order
    })


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
   

def remove_from_cart(request, key):

    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]

    request.session['cart'] = cart

    return redirect('cart')


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


def shop(request):

    products = Product.objects.all()
    supplements = Supplement.objects.all()

    items = []

    for p in products:
        items.append({
            "id": p.id,
            "type": "product",
            "name": p.name,
            "price": p.price,
            "old_price": p.old_price,
            "rating": p.rating,
            "image": p.image
        })

    for s in supplements:
        items.append({
            "id": s.id,
            "type": "supplement",
            "name": s.name,
            "price": s.price,
            "old_price": s.old_price,
            "rating": s.rating,
            "image": s.image
        })

    # SEARCH
    search = request.GET.get('search')
    if search:
        items = [i for i in items if search.lower() in i['name'].lower()]

    # SORT
    sort = request.GET.get('sort')

    if sort == "low":
        items = sorted(items, key=lambda x: x['price'])

    if sort == "high":
        items = sorted(items, key=lambda x: x['price'], reverse=True)

    # PAGINATION
    paginator = Paginator(items, 8)
    page = request.GET.get('page')

    items = paginator.get_page(page)

    context = {
        "items": items
    }

    return render(request, "shop.html", context)


def shop1(request):
    Supplements = Supplement.objects.all()
    return render(request, 'shop1.html', {'supplements': Supplements})


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


# ---------------- UPDATE QTY ----------------

def update_cart(request, key):
    cart = request.session.get('cart', {})

    qty = int(request.GET.get('qty', 1))

    if key in cart:
        cart[key]['qty'] = max(1, qty)

    request.session['cart'] = cart
    return redirect('cart')



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
            return redirect('shop')
        else:
            messages.error(request, 'Invalid login details')

    return render(request, 'login.html')
 
# -------------------------------
# Logout
# -------------------------------
def user_logout(request):
    logout(request)
    return redirect('login')





