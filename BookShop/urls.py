from django.contrib import admin
from shop.views import CustomLoginView, CustomLogoutView, signup_view
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# مسیرهای اصلی پروژه
urlpatterns = [
    path('admin/', admin.site.urls),    
    path('', include('shop.urls')),    

    # مسیرهای احراز هویت با ویوهای سفارشی
    path('login/', CustomLoginView.as_view(template_name='shop/login.html'), name='login'), 
    path('logout/', CustomLogoutView.as_view(), name='logout'),  
    path('signup/', signup_view, name='signup'),   
]

# در حالت توسعه، فعال‌سازی نمایش فایل‌های رسانه‌ای از مسیر media
if  settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





