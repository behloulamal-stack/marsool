from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category, StoreInformation, StoreContactInformation, Store, Owner
from .validators import validate_commercial_registration_format


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class StoreInformationSerializer(serializers.ModelSerializer):
    commercial_registration_number = serializers.CharField(
        max_length=30,
        validators=[
            validate_commercial_registration_format,
            UniqueValidator(queryset=StoreInformation.objects.all())
        ]
    )

    class Meta:
        model = StoreInformation
        fields = [
            'id', 'trade_name', 'commercial_registration_number',
            'category', 'nation', 'wilaya', 'location',
            'is_tax_registered', 'tax_document'
        ]

    def validate(self, data):
        is_tax_registered = data.get(
            'is_tax_registered',
            self.instance.is_tax_registered if self.instance else False
        )
        tax_document = data.get(
            'tax_document',
            self.instance.tax_document if self.instance else None
        )
        if is_tax_registered and not tax_document:
            raise serializers.ValidationError({
                "tax_document": "وثيقة التسجيل الضريبي مطلوبة إذا كانت المنشأة مسجلة في الضرائب."
            })
        return data


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        exclude = ['store_contact_information']


class StoreContactInformationSerializer(serializers.ModelSerializer):
    owners = OwnerSerializer(many=True)

    class Meta:
        model = StoreContactInformation
        fields = ['id', 'number_of_owners', 'owners']

    def validate(self, data):
        number_of_owners = data.get('number_of_owners')
        owners = data.get('owners', [])

        # التحقق إن عدد المالكين يطابق عدد البيانات المرسلة
        if number_of_owners != len(owners):
            raise serializers.ValidationError({
                "owners": (
                    f"عدد المالكين المدخل ({number_of_owners}) "
                    f"لا يطابق عدد بيانات المالكين المرسلة ({len(owners)})."
                )
            })

        return data

    def create(self, validated_data):
        owners_data = validated_data.pop('owners')
        store_contact = StoreContactInformation.objects.create(**validated_data)

        # bulk_create أسرع من حلقة create() لكل مالك على حدة
        Owner.objects.bulk_create([
            Owner(store_contact_information=store_contact, **owner_data)
            for owner_data in owners_data
        ])
        return store_contact


class StoreSerializer(serializers.ModelSerializer):
    """للعرض فقط (GET) — التاجر يشوف حالة متجره"""
    store_information = StoreInformationSerializer(read_only=True)
    store_contact_information = StoreContactInformationSerializer(read_only=True)

    class Meta:
        model = Store
        fields = [
            'id', 'store_information', 'store_contact_information',
            'status', 'created_at', 'reviewed_at'
        ]
        read_only_fields = ['status', 'created_at', 'reviewed_at']


class StoreApplicationSerializer(serializers.Serializer):
    """
    للإنشاء فقط (POST) — يستقبل معلومات المتجر والمالكين معاً
    ويخلق Store كاملة بضربة واحدة بحالة pending.
    """
    store_information = StoreInformationSerializer()
    store_contact_information = StoreContactInformationSerializer()

    def create(self, validated_data):
        info_data    = validated_data.pop('store_information')
        contact_data = validated_data.pop('store_contact_information')

        store_info    = StoreInformationSerializer().create(info_data)
        store_contact = StoreContactInformationSerializer().create(contact_data)

        store = Store.objects.create(
            store_information=store_info,
            store_contact_information=store_contact,
            status='pending'
        )
        return store