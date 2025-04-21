from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from datetime import timedelta


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


class OneTimeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='one_time_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Проверка истечения срока действия кода (через 2 минуты)
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"Код для {self.user.username}: {self.code}"

# обявления
class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    content = RichTextUploadingField()  # WYSIWYG-поле с HTML

    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements')

    def __str__(self):
        return self.title

#отклик
class Response(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE,
                                      related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Отклик от {self.author.username} на "{self.advertisement.title}"'

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




