from celery import shared_task
from django.utils import timezone
from accounts.models import CustomUser

@shared_task(queue= 'accounts')
def remove_expired_users():
    current_time = timezone.now()
    expired_users = CustomUser.objects.filter(verification_expires_at__lt=current_time)
    expired_users.delete()