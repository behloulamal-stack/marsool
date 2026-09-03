import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError

from .models import OTPVerification
from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    CompleteProfileSerializer,
    issue_tokens_for_user,
)
from .registration_token import RegistrationToken
from .rate_limit import check_otp_rate_limit, OTPRateLimitExceeded


# ----------------------------------------------------------------
# الأرقام التجريبية الثابتة للمسابقة والتجربة
# ----------------------------------------------------------------
TEST_PHONES = {
    "0500000001": "123456",
    "+213500000001": "123456",

    "0500000002": "123456",
    "+213500000002": "123456",

    "0500000003": "123456",
    "+213500000003": "123456",
}


# ================================================================
# الخطوة 1: طلب OTP
# ================================================================
class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        # 1. إذا كان الرقم تجريبياً: نتجاوز الـ Rate Limit
        if phone_number not in TEST_PHONES:
            try:
                check_otp_rate_limit(phone_number)
            except OTPRateLimitExceeded as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # 2. إذا كان الرقم تجريبياً: نستخدم الكود الثابت "123456"، وإلا نولد كود عشوائي
        if phone_number in TEST_PHONES:
            raw_otp = TEST_PHONES[phone_number]
        else:
            raw_otp = str(secrets.randbelow(900000) + 100000)

        # حفظ الكود في قاعدة البيانات
        OTPVerification.generate_for(phone_number, raw_otp)

        print(f"\n--- [SMS Simulation] ---")
        print(f"الرقم: {phone_number} | الكود: {raw_otp}")
        print(f"------------------------\n")

        return Response(
            {"detail": "تم إرسال رمز التحقق إلى رقم هاتفك."},
            status=status.HTTP_200_OK
        )


# ================================================================
# الخطوة 2: التحقق من OTP
# ================================================================
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        is_new_user  = serializer.validated_data['new_user']

        if is_new_user:
            reg_token = RegistrationToken.for_phone(phone_number)
            return Response({
                "new_user": True,
                "registration_token": str(reg_token),
                "message": "كود صحيح، أكمل إدخال بياناتك لإنشاء الحساب."
            }, status=status.HTTP_200_OK)

        user   = serializer.validated_data['user']
        tokens = issue_tokens_for_user(user)
        tokens["new_user"] = False
        return Response(tokens, status=status.HTTP_200_OK)


# ================================================================
# الخطوة 3: إكمال البيانات
# ================================================================
class CompleteProfileView(APIView):
    permission_classes     = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw_token = self._extract_bearer_token(request)
        if not raw_token:
            return Response(
                {"detail": "registration_token مطلوب في Authorization header."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            reg_token = RegistrationToken(raw_token)
        except TokenError as e:
            return Response(
                {"detail": f"الرمز غير صالح أو منتهي الصلاحية: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token_phone = reg_token['phone_number']
        body_phone  = request.data.get('phone_number')

        if token_phone != body_phone:
            return Response(
                {"detail": "رقم الهاتف لا يطابق الرمز المستخدم."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompleteProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = issue_tokens_for_user(user)
        tokens["new_user"] = False
        return Response(tokens, status=status.HTTP_201_CREATED)

    @staticmethod
    def _extract_bearer_token(request):
        header = request.headers.get('Authorization', '')
        if header.startswith('Bearer '):
            return header.split(' ', 1)[1]
        return None