from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse


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

# обявления
class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    content = models.TextField()
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

#рассылка
class Mailing(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Mailing')

    def __str__(self):
        return self.title






