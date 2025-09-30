from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from .models import Book, CustomUser, ContactMessage, TeamMember, Order, OrderItem, Review, WishlistItem
from django.utils.html import format_html
from django.templatetags.static import static

# پنل مدیریت برای مدل کاربر سفارشی
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    readonly_fields = ['date_joined']
    
    # افزودن فیلد شماره تماس به فرم‌های ویرایش و افزودن کاربر
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تماس', {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تماس', {'fields': ('phone_number',)}),
    )

# نمایش نقدها به‌صورت خطی در جزئیات کتاب
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = True
    show_change_link = False

# پنل مدیریت برای مدل کتاب
@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:red;">ناموجود</span>')
        elif obj.stock < 5:
            return format_html('<span style="color:orange;">کم ({})</span>', obj.stock)
        return obj.stock
    
    stock_status.short_description = 'وضعیت موجودی'
    
    # نمایش تصویر جلد یا تصویر دیفالت در لیست کتاب‌ها 
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:100px; border-radius:4px;" />',
                obj.cover.url
            )
        default_url = static('images/default_cover.jpg')
        return format_html(
            '<img src="{}" style="height:100px; border-radius:4px;" />',
            default_url
        )
    list_display = [
        'title', 'author', 'translator', 'publisher',
        'publication_year', 'category', 'price',
        'stock', 'stock_status',
        'created_at', 'cover_preview', 'is_featured', 'is_popular'
    ]
    search_fields = [
        'title', 'author', 'translator', 'publisher',
        'category', 'is_featured', 'is_popular'
    ]
    list_filter = [
        'author', 'translator', 'publisher',
        'category', 'price', 'created_at'
    ]
    ordering = ['-created_at']
    inlines = [ReviewInline]

    # گروه‌بندی فیلدها در فرم ویرایش کتاب
    fieldsets = (
        ('اطلاعات عمومی', {
            'fields': (
                'title', 'author', 'translator',
                'publisher', 'category',
                'is_featured', 'is_popular'
            )
        }),
        ('جزئیات کتاب', {
            'fields': (
                'price', 'publication_year',
                'page_count', 'introduction', 'cover',
                'stock'
            )
        }),
    )

# پنل مدیریت برای پیام‌های ارتباط با ما
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email', 'message']

# پنل مدیریت برای اعضای تیم فروشگاه
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'short_description', 'avatar_preview']
    exclude = ['order']

    # نمایش خلاصه توضیح در لیست
    def short_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = 'توضیح کوتاه'

    # نمایش آواتار یا تصویر دیفالت در لیست اعضای تیم
    def avatar_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
                obj.photo.url
            )
        default_url = static('images/default_profile.png')
        return format_html(
            '<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
            default_url
        )

# پنل مدیریت برای نقدهای کاربران
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'rating', 'created_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']
    list_editable = ['rating']
    ordering = ['-created_at']

# نمایش آیتم‌های سفارش به‌صورت خطی در جزئیات سفارش
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'quantity']
    can_delete = False
    show_change_link = False

# پنل مدیریت برای سفارش‌ها
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    inlines = [OrderItemInline]

    # شمارش تعداد آیتم‌های هر سفارش
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'تعداد آیتم‌ها'

# پنل مدیریت برای آیتم‌های علاقه‌مندی کاربران
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'added_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['added_at']

