from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('يجب إدخال رقم الهاتف')
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(phone_number=phone_number, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'عميل'),
        ('driver', 'سائق'),
        ('merchant', 'تاجر/مطعم'),
        ('admin', 'مدير النظام'),
    )
    GENDER_CHOICES = (
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    )

    phone_number = models.CharField(max_length=15, unique=True, verbose_name="رقم الهاتف")
    full_name = models.CharField(max_length=150, verbose_name="الاسم الكامل")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='customer', verbose_name="نوع الحساب")
 
 
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="الجنس")

    is_verified = models.BooleanField(default=False, verbose_name="تم التحقق عبر OTP")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
class OTPVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0) 
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
        ]

    @classmethod
    def generate_for(cls, phone_number, raw_otp):
      
        cls.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        
        return cls.objects.create(
            phone_number=phone_number,
            otp_hash=make_password(raw_otp),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, raw_otp):
        if self.is_used or self.is_expired():
            return False, "الرمز منتهي الصلاحية أو تم استخدامه سابقاً."
            
        if self.attempts >= 5:
            self.is_used = True
            self.save()
            return False, "تم تجاوز الحد الأقصى للمحاولات الخاطئة. اطلب رمزاً جديداً."
            
        if check_password(raw_otp, self.otp_hash):
            self.is_used = True
            self.save()
            return True, "تم التحقق بنجاح."
            
        self.attempts += 1
        self.save()
        return False, f"رمز خاطئ. المحاولات المتبقية: {5 - self.attempts}"