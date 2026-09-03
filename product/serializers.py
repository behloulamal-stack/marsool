from rest_framework import serializers
from .models import Menu, Product, OptionGroup, Option

# ===== إنشاء (Write) =====

class MenuWriteSerializer(serializers.ModelSerializer):
    """خطوة 1: التاجر يخلق قائمة (اسم بس)"""
    class Meta:
        model = Menu
        fields = ['id', 'name']


class OptionGroupWriteSerializer(serializers.ModelSerializer):
    """خطوة 2أ: التاجر يخلق مجموعة خيارات فارغة (مثلاً 'الإضافات')"""
    class Meta:
        model = OptionGroup
        fields = ['id', 'name']


class OptionWriteSerializer(serializers.ModelSerializer):
    """خطوة 2ب: التاجر يضيف خيار جوه مجموعة معينة (مثلاً 'جبنة' جوه 'الإضافات')"""
    class Meta:
        model = Option
        fields = ['id', 'option_group', 'name', 'price', 'calories']

    def validate_option_group(self, group):
        request = self.context['request']
        if group.store != request.user.store:
            raise serializers.ValidationError("هذه المجموعة لا تخص متجرك")
        return group


class ProductWriteSerializer(serializers.ModelSerializer):
    """خطوة 3: إنشاء المنتج + اختيار options محددة (صلصة بلا جبنة مثلاً) + اختيار menu"""
    options = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'calories', 'menu', 'options']

    def validate_menu(self, menu):
        request = self.context['request']
        user_store = getattr(request.user, 'store', None)
        if not user_store or menu.store != user_store:
            raise serializers.ValidationError("هذه القائمة لا تخص متجرك")
        return menu

    def validate_options(self, options):
        request = self.context['request']
        invalid = [o for o in options if o.option_group.store != request.user.store]
        if invalid:
            raise serializers.ValidationError("بعض الخيارات المحددة لا تخص متجرك")
        return options

    def create(self, validated_data):
        options = validated_data.pop('options', [])
        product = Product.objects.create(**validated_data)
        product.options.set(options)
        return product


# ===== عرض (Read) =====

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'name', 'price', 'calories']


class OptionGroupSerializer(serializers.ModelSerializer):
    """يعرض المجموعة مع كل خياراتها المتاحة (للتاجر يختار منها عند إنشاء منتج)"""
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = OptionGroup
        fields = ['id', 'name', 'options']

class ProductSerializer(serializers.ModelSerializer):
    grouped_options = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'menu', 'description', 'price', 'image', 'calories', 'grouped_options']

    def get_grouped_options(self, product):
        # إصلاح: .all() فقط — الاعتماد على الـ prefetch_related الموجود بالـ view
        # بدل .select_related() اللي كان يلغي الـ cache ويسبب N+1
        result = {}
        for option in product.options.all():
            group_name = option.option_group.name
            result.setdefault(group_name, []).append(OptionSerializer(option).data)
        return result


        
class MenuReadSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model  = Menu
        fields = ['id', 'name', 'products']