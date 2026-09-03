from django.contrib.gis.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    image = models.ImageField(upload_to="category/", null=True, blank=True, verbose_name="صورة الفئة")

    def __str__(self):
        return self.name


class StoreInformation(models.Model):
    NATION_CHOICES = [
        ('الجزائر', 'Alger'),
    ]
    WILAYA_CHOICES = [
        ('45', 'النعامة / Naâma'),
        ('16', 'الجزائر / Alger'),
        ('31', 'وهران / Oran'),
    ]

    trade_name = models.CharField(max_length=100, verbose_name="اسم المؤسسة التجارية")
    commercial_registration_number = models.CharField(
        max_length=30, unique=True, verbose_name="رقم السجل التجاري"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='stores_information',
        verbose_name="فئة المتجر"
    )
    nation = models.CharField(max_length=10, choices=NATION_CHOICES, verbose_name="الدولة")
    wilaya = models.CharField(max_length=2, choices=WILAYA_CHOICES, verbose_name="الولاية")
    location = models.PointField(geography=True, null=True, blank=True, verbose_name="موقع المتجر")
    is_tax_registered = models.BooleanField(default=False, verbose_name="منشأتك مسجلة في الضرائب")
    tax_document = models.FileField(
        upload_to="tax_documents/", null=True, blank=True,
        verbose_name="وثيقة التسجيل الضريبي"
    )

    def __str__(self):
        return self.trade_name


class StoreContactInformation(models.Model):
    number_of_owners = models.PositiveSmallIntegerField(default=1, verbose_name="عدد المالكين")

    def __str__(self):
        return f"معلومات اتصال ({self.number_of_owners} مالك)"


class Owner(models.Model):
    store_contact_information = models.ForeignKey(
        StoreContactInformation, on_delete=models.CASCADE, related_name='owners'
    )
    founder_name = models.CharField(max_length=150, verbose_name="اسم المالك")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="رقم الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    position = models.CharField(max_length=120, verbose_name="المنصب")

    def __str__(self):
        return f"{self.founder_name} ({self.phone_number})"


class Store(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='store'
    )
    store_information = models.OneToOneField(
        StoreInformation, on_delete=models.CASCADE, related_name='store'
    )
    store_contact_information = models.OneToOneField(
        StoreContactInformation, on_delete=models.CASCADE, related_name='store'
    )

    def __str__(self):
        return self.store_information.trade_name