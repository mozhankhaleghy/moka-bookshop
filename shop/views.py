from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages 
from . models import Book, TeamMember, CartItem, Order, OrderItem, Review, WishlistItem
from django.core.mail import EmailMessage, get_connection
from . forms import BookForm, BookSearchForm, SignUpForm, AuthenticationForm, ContactModelForm, EditProfileForm, ReviewForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from shop.utils.converters import to_persian_number
from django.db.models import  Q
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
import httpx

# فیلتر کردن کتاب‌ها بر اساس فرم جستجو
def get_filtered_books(request):
    form = BookSearchForm(request.GET)
    books = Book.objects.all()

    if form.is_valid():
        data = form.cleaned_data
        filters = {}

        # اعمال فیلترهای مختلف
        if data.get('q'):
            filters['title__icontains'] = data['q']
        if data.get('author'):
            filters['author__icontains'] = data['author']
        if data.get('translator'):
            filters['translator__icontains'] = data['translator']
        if data.get('publisher'):
            filters['publisher__icontains'] = data['publisher']
        if data.get('category'):
            filters['category'] = data['category']
        if data.get('min_price'):
            filters['price__gte'] = data['min_price']
        if data.get('max_price'):
            filters['price__lte'] = data['max_price']

        books = books.filter(**filters)

        # مرتب‌سازی معتبر
        valid_sort_fields = ['title', '-publication_year', 'price', '-price']
        if data.get('sort') in valid_sort_fields:
            books = books.order_by(data['sort'])

    else:
        books = Book.objects.none()
        messages.error(request, 'فیلتر جستجو نامعتبر بود.')

    return books, form

# ثبت‌نام کاربر جدید
def signup_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'شما قبلاً وارد شده‌اید.')
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            #  ورود خودکار پس از ثبت‌نام
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1') 
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'ثبت‌نام با موفقیت انجام شد و وارد شدید.')
                return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'shop/signup.html', {'form': form})

# "ورود سفارشی با گزینه "مرا به خاطر بسپار
class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'shop/login.html'

    def form_valid(self, form):
        remember = self.request.POST.get('remember_me')
        login(self.request, form.get_user())
        
        # تنظیم مدت اعتبار نشست
        if remember:
            self.request.session.set_expiry(604800)   # 7 روز
        else:
            self.request.session.set_expiry(0)    # بستن مرورگر
        
        messages.success(self.request, f"{form.get_user().username} عزیز، خوش آمدی!")
        response = redirect(self.get_success_url())

        # مدیریت کوکی remember_me
        if remember:
            response.set_cookie('remember_me', 'checked', max_age=604800)
        else:
            response.delete_cookie('remember_me')
        return response
    
    def get_initial(self):
        initial = super().get_initial()
        if self.request.COOKIES.get('remember_me') == 'checked':
            initial['remember_me'] = True
            return initial
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['remember_me_checked'] = self.request.COOKIES.get('remember_me') == 'checked'
        return context

    def get_success_url(self):
        return reverse('home')

# خروج سفارشی با پیام موفقیت
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "با موفقیت خارج شدید.")
        return super().dispatch(request, *args, **kwargs)

# نمایش پروفایل کاربر
@login_required(login_url='login')
def profile_view(request):
    user = request.user
    return render(request, 'shop/profile.html', {'user': user})

# ویرایش اطلاعات پروفایل
@login_required(login_url='login')
def edit_profile_view(request):
    user = request.user
    form = EditProfileForm(instance=user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    return render(request, 'shop/edit_profile.html', {'form': form})

# نمایش صفحه عدم دسترسی برای کاربران بدون مجوز
def unauthorized_view(request):
    return render(request, 'shop/unauthorized.html')

# صفحه اصلی سایت
@login_required(login_url='login')
def home_view(request):
    latest_books = Book.objects.filter(is_featured=True)[:6]
    popular_books = Book.objects.filter(is_popular=True)[:4]

    return render(request, 'shop/home.html', {
        'latest_books': latest_books,
        'popular_books': popular_books
    })

# صفحه درباره ما
def about_view(request):
    return render(request, 'shop/about.html')

# فرم ارتباط با ما + ارسال ایمیل
def contact_view(request):
    form = ContactModelForm(request.POST or None)
    if form.is_valid():
        contact = form.save()

        # اتصال به SMTP برای ارسال ایمیل
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=settings.CONTACT_EMAIL_USER,
            password=settings.CONTACT_EMAIL_PASSWORD,
            use_tls=True
        )

        email = EmailMessage(
            subject=f"پیام جدید از {contact.name}",
            body=contact.message,
            from_email=settings.CONTACT_EMAIL_USER,
            to=['mokabookcontact@gmail.com'],
            reply_to=[contact.email],
            connection=connection
        )
        email.send()

        messages.success(request, 'پیام شما با موفقیت ارسال شد')
        return redirect('contact')

    return render(request, 'shop/contact.html', {'form': form})

# صفحه سیاست حفظ حریم خصوصی
def privacy_view(request):
    return render(request, 'shop/privacy.html')

# نمایش اعضای تیم
def team_view(request):
    team_members = TeamMember.objects.all().order_by('order')
    return render(request, 'shop/team.html', {'team_members': team_members})

# نمایش لیست کتاب‌ها 
@login_required(login_url='login')
def book_list(request):
    books, form = get_filtered_books(request)

    # فیلتر قیمت حداکثری از GET
    max_price = request.GET.get('max_price')
    if max_price:
        try:
            max_val = int(max_price)
            books = books.filter(price__lte=max_val)
        except ValueError:
            pass

    return render(request, 'shop/book_list.html', {'form': form, 'books': books})

# نمایش جزئیات کتاب
@login_required(login_url='login')
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # نمایش کتاب‌های مرتبط بر اساس نویسنده، مترجم یا دسته‌بندی
    related_books = Book.objects.filter(
        Q(author=book.author) |
        Q(translator=book.translator) |
        Q(category=book.category)
    ).exclude(pk=book.pk).distinct()[:4]

    context = {
        'book': book,
        'related_books': related_books,
        'back_url': request.GET.get('next', request.META.get('HTTP_REFERER', reverse('home')))
    }

    # بررسی علاقه‌مندی کاربر
    if request.user.is_authenticated:
        is_in_wishlist = WishlistItem.objects.filter(user=request.user, book=book).exists()
        context['is_in_wishlist'] = is_in_wishlist

    return render(request, 'shop/book_detail.html', context)

# افزودن کتاب جدید
@permission_required('shop.add_book', login_url='unauthorized')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()  
            messages.success(request, f'کتاب "{book.title}" با موفقیت اضافه شد!')
            return redirect('home')
    else:
        form = BookForm()  

    return render(request, 'shop/add_book.html', {'form': form})

# ویرایش کتاب
@permission_required('shop.change_book', login_url='unauthorized')
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'کتاب "{book.title}" با موفقیت ویرایش شد!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
        
    return render(request, 'shop/edit_book.html', {'form': form})

# حذف کتاب
@permission_required('shop.delete_book', login_url='unauthorized')
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'کتاب «{title}» با موفقیت حذف شد!')
        return redirect('book_list') 

    return redirect('book_detail', pk=pk)

# نمایش کتاب‌های خریداری‌شده توسط کاربر
@login_required(login_url='login')
def my_books_view(request):
    paid_orders = Order.objects.filter(user=request.user, status='paid')
    purchased_items = OrderItem.objects.filter(order__in=paid_orders).select_related('book')
    books = [item.book for item in purchased_items]

    return render(request, 'shop/my_books.html', {'books': books})

# نمایش لیست علاقه‌مندی‌های کاربر
@login_required(login_url='login')
def wishlist_view(request):
    wishlist = WishlistItem.objects.filter(user=request.user)
    wishlist_count = to_persian_number(wishlist.count())
    return render(request, 'shop/wishlist.html', {
        'wishlist': wishlist,
        'wishlist_count': wishlist_count
    })

# افزودن یا حذف کتاب از علاقه‌مندی‌ها
@login_required(login_url='login')
def toggle_wishlist(request, pk):
    book = get_object_or_404(Book, pk=pk)
    item = WishlistItem.objects.filter(user=request.user, book=book).first()

    if item:
        item.delete()
        messages.success(request, "کتاب از علاقه‌مندی‌ها حذف شد.")
    else:
        WishlistItem.objects.create(user=request.user, book=book)
        messages.success(request, "کتاب به علاقه‌مندی‌ها اضافه شد.")

    return redirect('book_detail', pk=pk)

# افزودن نقد برای کتاب
@login_required(login_url='login')
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, "نقد شما ثبت شد.")
            return redirect('book_detail', pk=book.pk)
    else:
        form = ReviewForm()
    return render(request, 'shop/add_review.html', {'form': form, 'book': book})

# ویرایش نقد
@login_required(login_url='login')
def edit_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    form = ReviewForm(instance=review)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "نقد با موفقیت ویرایش شد.")
            return redirect('my_reviews')

    return render(request, 'shop/edit_review.html', {'form': form})

# حذف نقد
@login_required(login_url='login')
def delete_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, "نقد با موفقیت حذف شد.")
        return redirect('my_reviews')
    return render(request, 'shop/delete_review.html', {'review': review})

# نمایش نقدهای کاربر
@login_required(login_url='login')
def my_reviews_view(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    reviews_count = to_persian_number(reviews.count())
    return render(request, 'shop/my_reviews.html', {
        'reviews': reviews,
        'reviews_count': reviews_count
    })

# نمایش سبد خرید
@login_required(login_url='login')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# افزودن کتاب به سبد خرید
@login_required(login_url='login')
def add_to_cart_view(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if book.stock == 0:
        messages.error(request, "این کتاب ناموجود است و قابل افزودن به سبد خرید نیست❌")
        return redirect('book_detail', pk=book.pk)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    request.user.update_cart_count()
    messages.success(request, "کتاب به سبد خرید اضافه شد✅")
    return redirect('book_detail', pk=book.pk)

# کاهش تعداد یک آیتم در سبد
@login_required(login_url='login')
def decrease_quantity(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart')

# حذف آیتم از سبد خرید
@login_required(login_url='login')
def remove_from_cart_view(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    request.user.update_cart_count()
    messages.success(request, "کتاب از سبد خرید حذف شد.")
    return redirect('cart')

# نمایش تأیید سفارش پس از پرداخت موفق
@login_required(login_url='login')
def order_confirmation(request):
    order_id = request.session.get('last_order_id')    # ذخیره‌شده در session پس از پرداخت
    return render(request, 'shop/order_confirmation.html', {'order_id': order_id})

# نمایش رسید سفارش برای کاربر
@login_required(login_url='login')
def order_receipt(request):
    order_id = request.GET.get('id') or request.session.get('last_order_id')
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    return render(request, 'shop/order_receipt.html', {'order': order})

# ارسال درخواست به زرین‌پال
@login_required(login_url='login')
def request_payment(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    if not cart_items.exists():
        return HttpResponse("❌ سبد خرید شما خالی است")
    
    # آماده‌سازی اطلاعات کاربر برای متادیتا
    mobile_number = request.user.phone_number
    if mobile_number:
        mobile_number = str(mobile_number)
    else:
        mobile_number = None  
    
    metadata = {"email": str(request.user.email)}
    
    if mobile_number:
        metadata["mobile"] = mobile_number
        
    # داده‌های درخواست پرداخت
    data = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": total_price,
        "callback_url": "http://127.0.0.1:8000/verify/",
        "description": "پرداخت سفارش فروشگاه MoKa",
        "metadata": metadata
    }

    # ارسال درخواست 
    try:
        response = httpx.post("https://sandbox.zarinpal.com/pg/v4/payment/request.json", json=data, timeout=10)
        result = response.json()
    except httpx.RequestError as e:
        return HttpResponse(f'❌ خطا در اتصال به زرین‌پال: {str(e)}')
    except Exception as e:
        return HttpResponse(f'❌ خطای غیرمنتظره: {str(e)}')

    # هدایت به صفحه پرداخت در صورت موفقیت
    if result.get("data", {}).get("code") == 100:
        authority = result["data"]["authority"]
        request.session['pending_authority'] = authority
        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{authority}')
    else:
        error_message = result.get("errors", {}).get("message", "خطای نامشخص")
        return HttpResponse(f'❌ خطا در پرداخت: {error_message}')

# تایید پرداخت پس از بازگشت از زرین‌پال
@login_required(login_url='login')
@transaction.atomic
def verify_payment(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    session_authority = request.session.get('pending_authority')

    if authority != session_authority:
        return HttpResponse('❌ پرداخت نامعتبر یا تکراری است')

    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    if status == 'NOK':
        return redirect('payment_cancelled')

    # حالت تست در DEBUG
    if settings.DEBUG and request.session.get('mock_payment'):
        request.session['last_order_id'] = 'mock'
        return redirect('order_confirmation')

    if status == 'OK':
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": total_price,
            "authority": authority
        }

        try:
            response = httpx.post("https://sandbox.zarinpal.com/pg/v4/payment/verify.json", json=data, timeout=10)
            result = response.json()
        except httpx.RequestError as e:
            return HttpResponse(f'❌ خطا در اتصال به زرین‌پال: {str(e)}')
        except Exception as e:
            return HttpResponse(f'❌ خطای غیرمنتظره: {str(e)}')

        if result.get("data", {}).get("code") == 100:

            if not cart_items.exists():
                return HttpResponse("❌ پرداخت موفق بود ولی سبد خرید خالی است")
            
            print(f"✅ تعداد آیتم‌های سبد خرید: {cart_items.count()}")

            del request.session['pending_authority']

            # ثبت سفارش
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='paid',
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity
                )

                # کاهش موجودی کتاب
                book = item.book
                if book.stock >= item.quantity:
                    book.stock -= item.quantity
                else:
                    book.stock = 0
                book.save()

            cart_items.delete()
            request.session['last_order_id'] = order.id
            return redirect('order_confirmation')

        else:
            error_message = result.get("errors", {}).get("message", "❌ خطای نامشخص در تأیید پرداخت")
            return HttpResponse(f'❌ پرداخت ناموفق: {error_message}')

    return HttpResponse('❌ وضعیت پرداخت نامعتبر است')

def payment_cancelled(request):
    return render(request, 'shop/payment_cancelled.html')

