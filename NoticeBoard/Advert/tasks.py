from celery import shared_task
from django.core.mail import send_mass_mail
from .models import Mailing
from django.contrib.auth import get_user_model

User = get_user_model()


from celery.result import AsyncResult

@shared_task
def send_mass_mailing(mailing_id):
    if AsyncResult(mailing_id).status == 'SUCCESS':
        return  # Не выполняем задачу, если она уже была выполнена

    mailing = Mailing.objects.get(id=mailing_id)
    users = User.objects.all().values_list('email', flat=True)

    messages = [
        (mailing.title, mailing.message, 'vasinevakatirina@yandex.ru', [email])
        for email in users if email
    ]
    send_mass_mail(messages, fail_silently=False)