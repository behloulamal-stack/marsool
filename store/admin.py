from django.contrib import admin
from django.utils.html import format_html
from .models import Store, StoreInformation, StoreContactInformation, Owner, Category


# ---- Inline: المالكين داخل StoreContactInformation ----
class OwnerInline(admin.TabularInline):
    model = Owner
    extra = 0
    fields = ['founder_name', 'phone_number', 'email', 'position']
    readonly_fields = ['phone_number']


# ================================================================
# الـ Store Admin — هنا يغير الادمين الـ status
# ================================================================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = [
        'get_trade_name', 'status_badge', 'get_wilaya',
        'get_owners_count', 'created_at', 'reviewed_at'
    ]
    list_filter = ['status', 'store_information__wilaya', 'created_at']
    search_fields = [
        'store_information__trade_name',
        'store_information__commercial_registration_number',
        'store_contact_information__owners__phone_number',
    ]
    readonly_fields = ['created_at', 'reviewed_at', 'user', 'store_information', 'store_contact_information']
    ordering = ['-created_at']

    fieldsets = (
        ('حالة الطلب', {
            'fields': ('status', 'reviewed_at', 'user'),
            'description': 'تغيير الحالة إلى "مقبول" سيُرسل SMS تلقائياً لجميع المالكين.'
        }),
        ('المعلومات المرتبطة', {
            'fields': ('store_information', 'store_contact_information'),
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    actions = ['approve_stores', 'reject_stores']

    @admin.action(description=' قبول المتاجر المحددة')
    def approve_stores(self, request, queryset):
        for store in queryset.filter(status='pending'):
            store.status = 'approved'
            store.save()  # الـ signal يشتغل هنا
        self.message_user(request, "تم قبول المتاجر المحددة وإرسال SMS للمالكين.")

    @admin.action(description=' رفض المتاجر المحددة')
    def reject_stores(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, "تم رفض المتاجر المحددة.")

    @admin.display(description='اسم المتجر')
    def get_trade_name(self, obj):
        return obj.store_information.trade_name

    @admin.display(description='الحالة')
    def status_badge(self, obj):
        colors = {
            'pending':  ('#f59e0b', 'قيد المراجعة'),
            'approved': ('#10b981', 'مقبول'),
            'rejected': ('#ef4444', 'مرفوض'),
        }
        color, label = colors.get(obj.status, ('#6b7280', obj.status))
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, label
        )

    @admin.display(description='الولاية')
    def get_wilaya(self, obj):
        return obj.store_information.get_wilaya_display()

    @admin.display(description='عدد المالكين')
    def get_owners_count(self, obj):
        return obj.store_contact_information.owners.count()


# ---- StoreInformation منفصل ----
@admin.register(StoreInformation)
class StoreInformationAdmin(admin.ModelAdmin):
    list_display = ['trade_name', 'commercial_registration_number', 'wilaya', 'category']
    search_fields = ['trade_name', 'commercial_registration_number']
    list_filter = ['wilaya', 'category', 'is_tax_registered']


# ---- StoreContactInformation مع المالكين inline ----
@admin.register(StoreContactInformation)
class StoreContactInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'number_of_owners']
    inlines = [OwnerInline]


# ---- Category ----
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# ---- Owner ----
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['founder_name', 'phone_number', 'email', 'position']
    search_fields = ['founder_name', 'phone_number']