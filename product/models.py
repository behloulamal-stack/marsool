from django.db import models
from django.conf import settings # إذا كان الـ store مربوطاً بالمستخدم

class Menu(models.Model):
    name = models.CharField(max_length=255)
    # بناءً على السريالايزر، القائمة مربوطة بمتجر (store)
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='menus') 
    # (ملاحظة: إذا كان المتجر موديل منفصل، غيّر AUTH_USER_MODEL إلى اسم موديل المتجر)

    def __str__(self):
        return self.name

class OptionGroup(models.Model):
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='option_groups')
    name = models.CharField(max_length=100, verbose_name="اسم قائمة الخيارات")

    def __str__(self):
        return self.name


class Option(models.Model):
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100, verbose_name="اسم الخيار")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الخيار")
    calories = models.PositiveIntegerField(null=True, blank=True, verbose_name="السعرات الحرارية")

    def __str__(self):
        return f"{self.option_group.name} - {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    calories = models.PositiveIntegerField(null=True, blank=True)
    options = models.ManyToManyField(Option, blank=True, related_name='products')  # ⬅️ التغيير الجوهري