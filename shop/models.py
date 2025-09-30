from django.db import models
from django.contrib.auth.models import AbstractUser

# مدل کاربر سفارشی با فیلدهای اضافی برای اطلاعات تماس و آدرس
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)   
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    cart_items_count = models.PositiveIntegerField(default=0)    

    def __str__(self):
        return self.username
    
    def update_cart_count(self):
        from shop.models import CartItem
        self.cart_items_count = CartItem.objects.filter(user=self).count()
        self.save(update_fields=['cart_items_count'])

# مدل کتاب با اطلاعات کامل و دسته‌بندی
class Book(models.Model):
    CATEGORY_CHOICES = [
    ('general', 'عمومی'),
    ('science', 'علمی'),
    ('novel', 'رمان'),
    ('history', 'تاریخی'),
    ('child_ya', 'کودک و نوجوان'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, db_index=True)
    translator = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=100, db_index=True)
    introduction = models.TextField()
    price = models.IntegerField(default=100000)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general', db_index=True)
    publication_year = models.PositiveIntegerField(default=1400)
    page_count = models.PositiveIntegerField(default=1)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, verbose_name="نمایش در بخش جدیدترین")
    is_popular = models.BooleanField(default=False, verbose_name="نمایش در بخش محبوب‌ترین")

    def __str__(self):
        return f"{self.title} - {self.publisher}"
    
    class Meta: 
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"

# مدل پیام‌های ارتباط با ما
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta: 
        verbose_name = "پیام"
        verbose_name_plural = "پیام‌ها"

# مدل اعضای تیم فروشگاه با ترتیب قابل تنظیم
class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
    
    class Meta: 
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"

# مدل آیتم‌های سبد خرید
class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.book.title} × {self.quantity}"

# مدل نقد و امتیاز کاربران برای کتاب‌ها
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)  
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating})"
    
    class Meta: 
        verbose_name = "نقد"
        verbose_name_plural = "نقدها"
    
# مدل سفارش‌های ثبت‌شده توسط کاربران
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('paid', 'پرداخت شده')], default='paid')

    def __str__(self):
        return f"سفارش {self.id} - {self.user.username}"

    class Meta: 
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

# آیتم‌های هر سفارش شامل کتاب و تعداد
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} × {self.quantity}"
    
# مدل علاقه‌مندی‌های کاربران به کتاب‌ها
class WishlistItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')   # جلوگیری از ثبت تکراری یک کتاب برای یک کاربر
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"

    def __str__(self):
        return f"{self.user.username} → {self.book.title}"
    

    

