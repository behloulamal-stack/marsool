from rest_framework_simplejwt.tokens import Token
from datetime import timedelta


class RegistrationToken(Token):
    """
    توكن مؤقت خاص بمرحلة "تأكيد الرقم تم، كمل بياناتك".

    لماذا منفصل عن AccessToken؟
    - token_type = 'registration' (وليس 'access')
    - JWTAuthentication يرفض تلقائيا أي توكن token_type != 'access'
    - يعني حتى لو حد حاول يستخدمه كـ Bearer token في endpoint
      محمي بـ IsAuthenticated، Django يرفضه بـ 401 تلقائيا
    - صلاحيته 10 دقائق فقط (وليس ساعات كـ access token العادي)
    """

    token_type = 'registration'
    lifetime   = timedelta(minutes=10)

    @classmethod
    def for_phone(cls, phone_number: str) -> 'RegistrationToken':
        """
        ينشئ توكن جديد يحمل رقم الهاتف المُتحقق منه.
        يُستدعى في VerifyOTPView بعد نجاح التحقق من OTP للمستخدم الجديد.

        مثال الاستخدام في الـ view:
            reg_token = RegistrationToken.for_phone(phone_number)
            return Response({"registration_token": str(reg_token)})
        """
        token = cls()
        token['phone_number'] = phone_number
        return token