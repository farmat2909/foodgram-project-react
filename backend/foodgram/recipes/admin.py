from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import (Favorite, Ingredient, IngredientAmountRecipe, Recipe,
                     ShopingCart, Tag)


class RequiredInlineFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = (
            super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        )
        if i < 1:
            form.empty_permitted = False
        return form


class IngredientInline(admin.TabularInline):
    model = IngredientAmountRecipe
    extra = 1
    formset = RequiredInlineFormSet


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


class ShopingCartAdmin(admin.ModelAdmin):
    """Админ панель списка покупок."""
    list_display = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель избранного."""
    list_display = ('user', 'recipe')


class IngredientAmountAdmin(admin.ModelAdmin):
    """Админ панель избранного."""
    list_display = ('ingredient', 'recipe', 'amount')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShopingCart, ShopingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientAmountRecipe, IngredientAmountAdmin)
