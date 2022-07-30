from django.contrib import admin

from .models import Follow, User


class UsersAdmin(admin.ModelAdmin):
    """Админ панель пользователя."""
    list_display = (
        'username', 'password', 'first_name', 'last_name', 'email'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = "-пусто-"


class FollowsAdmin(admin.ModelAdmin):
    """Админ панель подписок."""
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    search_fields = ('user', 'following')
    empty_value_display = "-пусто-"


admin.site.register(User, UsersAdmin)
admin.site.register(Follow, FollowsAdmin)
