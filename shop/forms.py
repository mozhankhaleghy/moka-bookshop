from django import forms
from . models import Book, CustomUser, ContactMessage, Review
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# فرم افزودن یا ویرایش کتاب در پنل مدیریت یا بخش‌های داخلی
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        labels = {
            'title': 'عنوان کتاب',
            'author': 'نویسنده',
            'translator': 'مترجم',
            'publisher': 'انتشارات',
            'introduction': 'معرفی',
            'cover': 'جلد کتاب',
            'category': 'دسته‌بندی',
            'publication_year': 'سال انتشار',
            'page_count': 'تعداد صفحات',
            'price': 'قیمت',
            'stock': 'موجودی',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'translator': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'introduction': forms.Textarea(attrs={'class': 'form-control'}),
            'cover': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        book = super().save(commit=False)

        # حذف تصویر جلد در صورت انتخاب گزینه حذف
        if self.cleaned_data.get('delete_cover') and book.cover:
            book.cover.delete(save=False)
            book.cover = None

        if commit:
            book.save()
        return book

# فرم جستجوی کتاب با فیلترهای اختیاری و مرتب‌سازی
class BookSearchForm(forms.Form):
    q = forms.CharField(required=False, label='عنوان کتاب',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    author = forms.CharField(required=False, label='نویسنده',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    translator = forms.CharField(required=False, label='مترجم',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    publisher = forms.CharField(required=False, label='ناشر',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(required=False, label='دسته‌بندی',
        widget=forms.Select(attrs={'class': 'form-control'}))
    min_price = forms.IntegerField(required=False, widget=forms.HiddenInput())
    max_price = forms.IntegerField(required=False, widget=forms.HiddenInput())
    sort = forms.ChoiceField(required=False, label='مرتب‌سازی',
        choices=[
            ('', 'همه موارد'),
            ('title', 'عنوان (الفبایی)'), 
            ('-publication_year', 'جدیدترین'),
            ('price', 'ارزان‌ترین'),
            ('-price', 'گران‌ترین'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # افزودن گزینه‌های دسته‌بندی از مدل Book
        self.fields['category'].choices = [('', 'همه دسته‌ها')] + Book.CATEGORY_CHOICES

# فرم ثبت‌نام کاربر جدید با اعتبارسنجی ایمیل تکراری
class SignUpForm(UserCreationForm):     
    email = forms.EmailField(
        label='ایمیل',
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    phone_number = forms.CharField(
        label='شماره موبایل',
        max_length=15, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label='نام کاربری',
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label='رمز عبور', 
        required=True, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label='تکرار رمز عبور', 
        required=True, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = CustomUser        

        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def clean_email(self):              
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("این ایمیل قبلا ثبت شده است.")
        return email

# فرم ورود با استایل سفارشی برای فیلدها
class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'نام کاربری'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        })

# فرم بازیابی رمز عبور با استایل‌دهی فارسی
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='ایمیل',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

# فرم تنظیم رمز جدید با اعتبارسنجی و ترجمه خطاها
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='تأیید رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
        strip=False,
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        self._validate_and_translate(password)
        return password

    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password2')
        self._validate_and_translate(password)
        return password

    def _validate_and_translate(self, password):               # ترجمه پیام‌های خطای اعتبارسنجی رمز عبور
        try:
            validate_password(password, self.user)
        except ValidationError as e:
            translated_errors = []
            for error in e.messages:
                if "This password is too common" in error:
                    translated_errors.append("این رمز عبور خیلی رایج است.")
                elif "This password is entirely numeric" in error:
                    translated_errors.append("رمز عبور نباید فقط عدد باشد.")
                elif "This password is too short" in error:
                    translated_errors.append("رمز عبور باید حداقل ۸ کاراکتر باشد.")
                else:
                    translated_errors.append(error)
            raise ValidationError(translated_errors)

    def clean(self):                # بررسی تطابق رمز عبور و تأیید آن
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمز عبور و تأیید آن یکسان نیستند.")
        return cleaned_data
    
# فرم مدل ارتباط با ما برای ارسال پیام به مدیر سایت
class ContactModelForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        labels = {
            'name': 'نام',
            'email': 'ایمیل',
            'message': 'پیام',
            }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ''}),
            }

# فرم ویرایش پروفایل کاربر با فیلدهای سفارشی
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number',
            'first_name', 'last_name', 'profile_image',
            'address', 'postal_code',
        ]
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'phone_number': 'شماره موبایل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'profile_image': 'عکس پروفایل',
            'address': 'آدرس',
            'postal_code': 'کد پستی',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

# فرم ثبت نقد و امتیاز برای کتاب‌ها
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'امتیاز',
            'comment': 'متن نقد',
        }
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control',
                'style': 'color:#2c3e50; font-weight:500;'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'color:#2c3e50; font-weight:500;',
                'placeholder': 'نظر خود را بنویسید...'
            }),
        }








