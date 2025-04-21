import random
import string
from django.core.mail import send_mail

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_registration_email(email, code):
    send_mail(
        'Код подтверждения регистрации',
        f'Ваш код: {code}',
        'vasinevakatirina@yandex.ru',
        [email],
    )