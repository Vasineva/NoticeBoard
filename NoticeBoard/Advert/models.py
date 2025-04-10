from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings

TANK = 'tank'
HEALER = 'healer'
DPS = 'dps'
TRADER = 'trader'
GUILD_MASTER = 'guildmaster'
QUEST_GIVER = 'questgiver'
BLACKSMITH = 'blacksmith'
LEATHERWORKER = 'leatherworker'
ALCHEMIST = 'alchemist'
SPELL_MASTER = 'spellmaster'

CATEGORY_CHOICES = [
    (TANK, 'Танки'),
    (HEALER, 'Хилы'),
    (DPS, 'ДД'),
    (TRADER, 'Торговцы'),
    (GUILD_MASTER, 'Гилдмастеры'),
    (QUEST_GIVER, 'Квестгиверы'),
    (BLACKSMITH, 'Кузнецы'),
    (LEATHERWORKER, 'Кожевники'),
    (ALCHEMIST, 'Зельевары'),
    (SPELL_MASTER, 'Мастера заклинаний'),
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Использование email для аутентификации
    REQUIRED_FIELDS = ['username']  # 'username' должен быть указан при создании суперпользователя

    def __str__(self):
        return self.username

class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    content = RichTextUploadingField()  # WYSIWYG-поле с HTML

    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='advertisements')

    def __str__(self):
        return self.title


class Response(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE,
                                      related_name='responses')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='responses')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Response by {self.author.username} on "{self.advertisement.title}"'


class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(blank=True, null=True)
    subscribers = models.ManyToManyField(User, through='NewsletterSubscription',
                                         related_name='subscriptions')

    def __str__(self):
        return self.subject

class Media(models.Model):
    advertisement = models.ForeignKey('Advertisement', on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='ads/media/', blank=True, null=True)
    media_type = models.CharField(
        max_length=10,
        choices=[('image', 'Изображение'), ('video', 'Видео')],
        blank=True,
        null=True  # Поле не обязательно для заполнения
    )

    def __str__(self):
        return f"{self.media_type or 'Без типа'} для {self.advertisement.title}"


class NewsletterSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} subscribed to {self.newsletter.subject}'