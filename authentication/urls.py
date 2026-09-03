from django.urls import path
from .views import (
    RequestOTPView,
    VerifyOTPView,
    CompleteProfileView,
)

urlpatterns = [
    # الخطوة 1: طلب OTP (جديد أو قديم، نفس الـ endpoint)
    path('auth/request-otp/', RequestOTPView.as_view(), name='request-otp'),

 
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    # الخطوة 3: إكمال البيانات (للمستخدم الجديد فقط)
    path('auth/complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
]