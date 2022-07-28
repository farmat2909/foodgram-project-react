from django.contrib import admin

from .models import Recipe, Tag, Ingredient, IngredientAmountRecipe, Favorite, ShopingCart


class IngredientInline(admin.TabularInline):
    model = IngredientAmountRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Админ панель рецепта."""
    inlines = (IngredientInline,)
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    """Админ панель ингредиентов."""
    inlines = (IngredientInline,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Админ панель ингредиентов."""
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShopingCart)
admin.site.register(Favorite)
admin.site.register(IngredientAmountRecipe)
