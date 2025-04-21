from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Response


@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    # Если отклик только что создан
    if created:
        # Отправить уведомление автору объявления
        send_mail(
            subject='Новый отклик на ваше объявление',
            message=(
                f'Пользователь {instance.author.username} откликнулся на ваше объявление "{instance.advertisement.title}".\n\n'
                f'Текст отклика:\n{instance.content}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.advertisement.author.email],
            fail_silently=True,
        )

    # Если отклик был принят
    if instance.is_accepted:
        # Отправить уведомление пользователю, оставившему отклик
        send_mail(
            subject='Ваш отклик принят!',
            message=(
                f'Ваш отклик на объявление "{instance.advertisement.title}" был принят автором.\n\n'
                f'Спасибо за участие!'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.author.email],
            fail_silently=True,
        )
