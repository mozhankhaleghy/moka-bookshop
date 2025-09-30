import jdatetime
from django import template

register = template.Library()    # ثبت کتابخانه فیلترها

@register.filter
def to_jalali(value, fmt="%Y/%m/%d"):
    """
    تبدیل تاریخ میلادی به تاریخ شمسی با فرمت دلخواه.
    استفاده در قالب:
        {{ some_date|to_jalali }}
        یا با فرمت سفارشی:
        {{ some_date|to_jalali:"%d %B %Y" }}
    """
    if not value:
        return "—"      # نمایش خط تیره در صورت نبود مقدار
    try:       
        # تبدیل تاریخ میلادی به شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime(fmt)
    except Exception:
        return "—"     # جلوگیری از خطا در قالب در صورت ورودی نامعتبر
    
