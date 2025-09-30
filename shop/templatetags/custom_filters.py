from django import template
from shop.utils.converters import to_persian_number

register = template.Library()     # ثبت کتابخانه فیلترها

# تعریف فیلتر سفارشی برای استفاده در قالب‌ها
@register.filter
def to_persian_number_filter(value):
    """
    تبدیل عدد انگلیسی به عدد فارسی برای نمایش در قالب‌ها.
    مثال استفاده در قالب:
        {{ some_number|to_persian_number_filter }}
    """
    return to_persian_number(value)




