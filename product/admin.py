from django.contrib import admin
from .models import Menu, Product, OptionGroup, Option


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'store')
   
    search_fields = ('name', 'store__store_information__trade_name') 


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu', 'price', 'calories')
    list_filter = ('menu',)
    search_fields = ('name',)


@admin.register(OptionGroup)
class OptionGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
   
    inlines = [OptionInline]


admin.site.register(Option)