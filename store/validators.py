import re
from rest_framework import serializers


def validate_commercial_registration_format(value):
    """
    يتحقق من صيغة رقم السجل التجاري الجزائري
    الصيغة التقريبية: 16/00-1234567B21
    """
    pattern = r'^\d{2}/\d{2}-\d{7}[A-Z]\d{2}$'
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            "صيغة رقم السجل التجاري غير صحيحة (مثال: 16/00-1234567B21)"
        )
    return value