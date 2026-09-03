import re
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, OTPVerification
from .registration_token import RegistrationToken


PHONE_REGEX = r'^\+?[0-9]{9,15}$'

TEST_PHONES = [
    "0500000001", "+213500000001",
    "0500000002", "+213500000002",
    "0500000003", "+213500000003",
]
# ================================================================
# 1. طلب OTP — شاشة موحدة للجديد والقديم
# ================================================================
class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if not re.match(PHONE_REGEX, value):
            raise serializers.ValidationError(
                "صيغة رقم الهاتف غير صحيحة. يجب أن يحتوي على أرقام فقط."
            )
        return value


# ================================================================
# 2. التحقق من OTP — "الشرطي الذكي"
# ================================================================
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code    = serializers.CharField(max_length=6, min_length=6)
    

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        otp_code     = attrs['otp_code']
        if phone_number in TEST_PHONES and otp_code == "123456":
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            attrs['new_user'] = (user is None)
            attrs['user'] = user
            return attrs

        otp_record = OTPVerification.objects.filter(
            phone_number=phone_number,
            is_used=False
        ).last()

        if not otp_record:
            raise serializers.ValidationError(
                {"otp_code": "لا يوجد رمز تفعيل نشط لهذا الرقم. اطلب رمزاً جديداً."}
            )

        is_valid, message = otp_record.verify(otp_code)
        if not is_valid:
            raise serializers.ValidationError({"otp_code": message})

        user = CustomUser.objects.filter(phone_number=phone_number).first()

        if user is not None:
            if not user.is_active:
                raise serializers.ValidationError(
                    {"phone_number": "هذا الحساب محظور من قبل الإدارة."}
                )
            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=['is_verified'])

        attrs['user']     = user
        attrs['new_user'] = user is None

        return attrs


# ================================================================
# 3. إكمال بيانات المستخدم الجديد (يُستخدم فقط لو new_user=True)
# ================================================================
class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ['phone_number', 'full_name', 'email', 'role', 'birth_date', 'gender']
        extra_kwargs = {
            'email':      {'required': False, 'allow_null': True},
            'role':       {'required': False},
            'birth_date': {'required': False, 'allow_null': True},
            'gender':     {'required': False, 'allow_null': True},
        }

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "هذا الرقم مسجل بالفعل. يرجى تسجيل الدخول."
            )
        return value

    def validate_email(self, value):
        return value or None

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            full_name=validated_data['full_name'],
            email=validated_data.get('email'),
            role=validated_data.get('role', 'customer'),
            birth_date=validated_data.get('birth_date'),
            gender=validated_data.get('gender'),
        )
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return user


# ================================================================
# دالة مساعدة مشتركة — تُستدعى من الـ view بعد نجاح العملية
# خارج الـ serializer لأن إصدار JWT ليس من مسؤولية الـ serializer
# ================================================================
def issue_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh['phone_number'] = user.phone_number
    refresh['role']         = user.role
    refresh['full_name']    = user.full_name
    refresh['is_verified']  = user.is_verified

    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
        'user': {
            'phone_number': user.phone_number,
            'full_name':    user.full_name,
            'role':         user.role,
            'is_verified':  user.is_verified,
        }
    }