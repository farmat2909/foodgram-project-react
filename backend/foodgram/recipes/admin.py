from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmountRecipe, Recipe,
                     ShopingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientAmountRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Админ панель рецепта."""
    inlines = (IngredientInline,)
    list_display = ('name', 'author', 'count_recipes_favorite')
    list_filter = ('author', 'name', 'tags')

    def count_recipes_favorite(self, obj):
        return obj.favorites.count()

    count_recipes_favorite.short_description = 'количество в избранном'


class IngredientAdmin(admin.ModelAdmin):
    """Админ панель ингредиентов."""
    inlines = (IngredientInline,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Админ панель тегов."""
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


class ShopingCartadmin(admin.ModelAdmin):
    """Админ панель списка покупок."""
    list_display = ('user', 'recipe')


class Favoriteadmin(admin.ModelAdmin):
    """Админ панель избранного."""
    list_display = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShopingCart, ShopingCartadmin)
admin.site.register(Favorite, Favoriteadmin)
admin.site.register(IngredientAmountRecipe)
