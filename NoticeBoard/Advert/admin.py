from django.contrib import admin
from .models import Advertisement, Media
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User  # импортируй свою модель


admin.site.register(Advertisement)
admin.site.register(Media)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_verified', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Личная информация'), {'fields': ('username',)}),
        (_('Разрешения'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'is_verified'),
        }),
    )
