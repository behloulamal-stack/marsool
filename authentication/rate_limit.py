from django.core.cache import cache


class OTPRateLimitExceeded(Exception):
    pass


def check_otp_rate_limit(phone_number):
    """
    ماكس 3 طلبات OTP لكل رقم هاتف خلال 10 دقائق.
    يستخدم Django cache (LocMemCache محليا، Redis في production).
    """
    cache_key = f"otp_rate_limit:{phone_number}"
    attempts  = cache.get(cache_key, 0)

    if attempts >= 3:
        raise OTPRateLimitExceeded(
            "لقد تجاوزت عدد المحاولات المسموحة. حاول مرة أخرى بعد 10 دقائق."
        )

    cache.set(cache_key, attempts + 1, timeout=600)