from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from .models import Store, Owner
from authentication.models import CustomUser  # عدلي المسار حسب اسم الـ app تاعك


@receiver(pre_save, sender=Store)
def on_store_approved(sender, instance, **kwargs):
    """
    يشتغل تلقائيا كل مرة يتحفظ فيها Store.
    إذا تغير status من pending/rejected إلى approved:
      1. يخلق CustomUser لكل Owner (إذا ماشي موجود)
    
      3. يبعت SMS لكل المالكين برابط الدخول
    """

    # نتجاهل إذا كان Store جديد (ما عندوش id بعد)
    if not instance.pk:
        return

    try:
        old_instance = Store.objects.get(pk=instance.pk)
    except Store.DoesNotExist:
        return

    # نتحققو: واش status تغير لـ approved الآن؟
    status_just_approved = (
        old_instance.status != 'approved' and
        instance.status == 'approved'
    )

    if not status_just_approved:
        return

    # ---- نجيبو كل المالكين ----
    owners = Owner.objects.filter(
        store_contact_information=instance.store_contact_information
    )

    for index, owner in enumerate(owners):
        user, created = CustomUser.objects.get_or_create(
            phone_number=owner.phone_number,
            defaults={
                'full_name': owner.founder_name,
                'email': owner.email if owner.email else None,
                'role': 'merchant',
                'is_verified': False,
                'is_active': True,
            }
        )
        if created:
            user.set_unusable_password()
            user.save()

        # أول مالك يربط بالـ Store
        if index == 0:
            instance.user = user
    # نسجلو وقت القبول
    instance.reviewed_at = timezone.now()

    # ---- نبعتو SMS لكل المالكين ----
    _send_approval_sms_to_owners(owners)


def _send_approval_sms_to_owners(owners):
    """
    يبعت SMS لكل مالك برابط الدخول.
    TODO: استبدل بـ Celery task + SMS gateway حقيقي.
    """
    login_url = f"{settings.FRONTEND_URL}/merchant/login"

    for owner in owners:
        message = (
            f"مرحباً {owner.founder_name}،\n"
            f"تم قبول طلب انضمام متجرك إلى منصتنا.\n"
            f"يمكنك الدخول عبر الرابط التالي:\n"
            f"{login_url}\n"
            f"أدخل رقم هاتفك {owner.phone_number} للمتابعة."
        )

        # TODO: استبدل هذا بـ SMS gateway حقيقي
        print(f"\n--- [SMS Simulation] ---")
        print(f"إلى: {owner.phone_number}")
        print(f"الرسالة:\n{message}")
        print(f"------------------------\n")