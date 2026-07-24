
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from .models import Brand, Product, CartItem, Wishlist, Order, Address, OrderItem
from .forms import SignUpForm, FeedbackForm, AddressForm
from fuzzywuzzy import fuzz
from django.db.models import Q
from django.http import JsonResponse
from .models import Product
import re


def home(request):
    mobile_brands = Brand.objects.all() 
    context = {
        'mobile_brands': mobile_brands
    }
    return render(request, 'home.html', context)


def products(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    products = Product.objects.filter(brand=brand)
    context = {
        'products': products,
        'brand': brand,
    }
    return render(request, 'products.html', context)


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context)


def increase_quantity(request, cart_item_id):
    cart_item = CartItem.objects.get(pk=cart_item_id)
    if cart_item.quantity < cart_item.product.stock_quantity:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


def decrease_quantity(request, cart_item_id):
    cart_item = CartItem.objects.get(pk=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    elif cart_item.quantity <= 1:
        cart_item.delete()
    return redirect('cart')


@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    return redirect('cart')


@login_required(login_url='/login/')
def cart(request):
    cart_items = CartItem.objects.all()
    total_cost = 0
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total_cost += item.subtotal

    context = {
        'cart_items': cart_items,
        'total_cost': total_cost
    }
    return render(request, 'cart.html', context)


@login_required(login_url='/login/')
def wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product_id)
        return redirect('wishlist')
    else:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        context = {'wishlist': wishlist}
        return render(request, 'wishlist.html', context)


@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        wishlist.save()
        return redirect('wishlist')
    else:
        return HttpResponse("Please login to add items to your wishlist.")


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)
    return redirect('wishlist')

@login_required(login_url='/login/')
def profile(request):
    saved = False
    max_addresses_reached = False
    user = request.user

    if request.method == 'POST':
        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            if Address.objects.filter(customer=user).count() < 3:
                address = address_form.save(commit=False)
                address.customer = user
                address.save()
                saved = True
            else:
                max_addresses_reached = True
    else:
        address_form = AddressForm()

    addresses = Address.objects.filter(customer=user)

    return render(request, 'profile.html', {
    'user': user,
    'address_form': address_form,
    'password_form': PasswordChangeForm(user),
    'saved': saved,
    'addresses': addresses,
    'max_addresses_reached': max_addresses_reached
})


def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_cost = 0
    for item in cart_items:
        total_cost += item.product.price * item.quantity

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            address = get_object_or_404(Address, id=selected_address_id)
        else:
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.customer = user
                address.save()
            else:
                address = None

        if address:
            order = Order.objects.create(user=user, address=address, price=total_cost, total_cost=total_cost)

            for cart_item in cart_items:
                OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()

            cart_items.delete()
            return redirect('payment_mode', order_id=order.id)
    else:
        form = AddressForm()

    addresses = Address.objects.filter(customer=user)

    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items, 'total_cost': total_cost, 'addresses': addresses})



def payment_mode(request, order_id):
    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        selected_payment_mode = request.POST.get('payment_mode')
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'payment_mode.html')


def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})


def view_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'invoice.html', {'order': order})


def contact(request):
    return render(request, 'contact.html')


def search_results(request):
    query = request.GET.get('query')
    results = None

    if query:
        fuzzy_results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(name__icontains=query.replace(' ', '')) |
            Q(name__icontains=query.lower())
        )

        similarity_scores = [
            (result, fuzz.token_set_ratio(query.lower(), result.name.lower()))
            for result in fuzzy_results
        ]

        sorted_results = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        results = [result for result, _ in sorted_results]

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_results.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/login/')
def my_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        if order.user == request.user and not order.is_cancelled:
            order.is_cancelled = True
            order.save()
            
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.product
                product.stock_quantity += order_item.quantity
                product.save()
                
            messages.success(request, 'Order cancelled successfully.')

    orders = Order.objects.filter(user=request.user)
    return render(request, 'my_orders.html', {'orders': orders})


def edit_address(request, address_id):
    address = Address.objects.get(id=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AddressForm(instance=address)

    return render(request, 'edit_address.html', {'form': form, 'address': address})


def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.delete()
    return redirect('profile')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import FeedbackForm

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.save()

            from_email = request.user.email
            to_email = 'sumanthking928@gmail.com'

            email_context = {
                'name': feedback.name,
                'email': feedback.email,
                'message': feedback.message
            }
            email_body = render_to_string('feedback_email.html', context=email_context)

            send_mail(
                'New Feedback Submission',
                'This is the plain text version of the email.',
                from_email,
                [to_email],
                html_message=email_body,  # Set the content type to text/html
                fail_silently=False,
            )

            return redirect('thank_you')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})


@login_required(login_url='/login/')
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.save()

            from_email = request.user.email
            to_email = 'sumanthking928@gmail.com'

            email_context = {
                'name': feedback.name,
                'email': feedback.email,
                'message': feedback.message
            }
            email_body = render_to_string('feedback_email.html', context=email_context)

            send_mail(
                'New Feedback Submission',
                email_body,
                from_email,
                [to_email],
                fail_silently=False,
            )

            return redirect('thank_you')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')

def ai_recommendation(request):

    products = Product.objects.none()
    brands = Brand.objects.all()

    if request.method == "POST":

        budget = request.POST.get("budget", "").strip()
        brand = request.POST.get("brand", "").strip()

        if budget:

            # Budget Range
            if "-" in budget:

                try:
                    min_budget, max_budget = map(int, budget.split("-"))

                    products = Product.objects.filter(
                        price__gte=min_budget,
                        price__lte=max_budget
                    )

                except:
                    products = Product.objects.none()

            # Single Budget
            else:

                try:
                    amount = int(budget)

                    products = Product.objects.filter(
                        price__lte=amount
                    )

                except:
                    products = Product.objects.none()

            # Brand Filter
            if brand:

                products = products.filter(
                    brand__name__iexact=brand
                )

            # AI Ranking
            products = products.order_by(
                "-camera_score",
                "-gaming_score",
                "-battery_score"
            )

    return render(
        request,
        "ai_recommendation.html",
        {
            "products": products,
            "brands": brands
        }
    )
from django.http import JsonResponse
from .models import Product
import google.generativeai as genai
import re

model = genai.GenerativeModel("gemini-2.5-flash")
def chatbot(request):

    message = request.GET.get("message", "").lower().strip()

    # Greetings

    greetings = {
        "hi": "👋 Hello! Welcome to Cell City. How can I help you today?",
        "hii": "👋 Hello! Welcome to Cell City. How can I help you today?",
        "hello": "👋 Hello! Welcome to Cell City. How can I help you today?",
        "hey": "👋 Hello! Welcome to Cell City. How can I help you today?",
        "good morning": "🌞 Good Morning! Welcome to Cell City.",
        "gm": "🌞 Good Morning! Welcome to Cell City.",
        "good afternoon": "☀️ Good Afternoon! How can I help you?",
        "good evening": "🌆 Good Evening! Welcome to Cell City.",
        "ge": "🌆 Good Evening! Welcome to Cell City.",
        "how are you": "😊 I'm doing great! How can I help you find the perfect mobile?",
        "thanks": "😊 You're welcome!",
        "thank you": "😊 You're welcome!",
        "thankyou": "😊 You're welcome!",
        "bye": "👋 Goodbye! Thanks for visiting Cell City.",
        "goodbye": "👋 Goodbye! Thanks for visiting Cell City."
    }

    if message in greetings:
        return JsonResponse({"response": greetings[message]})

    # Best Camera Phones

    if "best camera" in message:
        phones = Product.objects.order_by("-camera_score")[:5]

        answer = "📸 Best Camera Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - ₹{p.price}\n"

        return JsonResponse({"response": answer})

    # Best Gaming Phones

    if "best gaming" in message:
        phones = Product.objects.order_by("-gaming_score")[:5]

        answer = "🎮 Best Gaming Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - ₹{p.price}\n"

        return JsonResponse({"response": answer})

    # Best Battery Phones

    if "best battery" in message:
        phones = Product.objects.order_by("-battery_score")[:5]

        answer = "🔋 Best Battery Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - ₹{p.price}\n"

        return JsonResponse({"response": answer})

    # Best RAM Phones

    if "best ram" in message:
        phones = Product.objects.order_by("-ram")[:5]

        answer = "💾 Best RAM Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - {p.ram} RAM\n"

        return JsonResponse({"response": answer})

    # Best Processor Phones

    if "best processor" in message:
        phones = Product.objects.all()[:5]

        answer = "⚡ Top Processor Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - {p.processor}\n"

        return JsonResponse({"response": answer})

    # Budget Search

    budget_match = re.search(r'(\d{4,6})', message)

    if budget_match:
        budget = int(budget_match.group(1))

        phones = Product.objects.filter(
            price__lte=budget
        ).order_by("price")

        if phones.exists():

            answer = f"💰 Phones Under ₹{budget}:\n\n"

            for p in phones[:5]:
                answer += f"📱 {p.name} - ₹{p.price}\n"

            return JsonResponse({"response": answer})

    # 2026 Phones

    if "2026" in message:

        phones = Product.objects.filter(
            launch_year=2026
        )

        if phones.exists():

            answer = "🚀 Mobiles Launched in 2026:\n\n"

            for p in phones:
                answer += f"📱 {p.name} - ₹{p.price}\n"

            return JsonResponse({"response": answer})

    # Best Phones

    if "best mobile" in message or "best phone" in message:

        phones = Product.objects.order_by(
            "-camera_score",
            "-gaming_score",
            "-battery_score"
        )[:5]

        answer = "🏆 Top Phones:\n\n"

        for p in phones:
            answer += f"📱 {p.name} - ₹{p.price}\n"

        return JsonResponse({"response": answer})

    # Search by phone name

    products = Product.objects.filter(
        name__icontains=message
    )

    # Search by brand

    if not products.exists():

        brands = [
            "apple",
            "samsung",
            "oneplus",
            "vivo",
            "oppo",
            "realme",
            "redmi",
            "poco",
            "motorola",
            "iqoo",
            "nokia",
            "honor",
            "tecno"
        ]

        for brand in brands:

            if brand in message:

                products = Product.objects.filter(
                    brand__name__icontains=brand
                )

                break

    # Product Details

    if products.exists():

        product = products.first()

        answer = f"""
📱 {product.name}

💰 Price: ₹{product.price}
🔋 Battery: {product.battery}
📸 Camera: {product.camera}
⚡ Processor: {product.processor}
💾 RAM: {product.ram}
📂 Storage: {product.storage}
📅 Launch Year: {product.launch_year}
"""

        return JsonResponse({"response": answer})

    # Gemini Fallback

    prompt = f"""
You are Cell City AI Assistant.

Answer briefly in 3 lines.

Question:
{message}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 80
        }
    )

    return JsonResponse({
        "response": response.text
    })