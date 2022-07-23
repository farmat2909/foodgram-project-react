from django.core.validators import MinValueValidator, RegexValidator

from django.db import models

from users.models import User


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmountRecipe',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Рецепт'
    )
    image = models.ImageField(
        upload_to='recipe/'
    )
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        'Recipe',
        null=True,
        on_delete=models.SET_NULL,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f' У пользователя {self.user} в избранном рецепт {self.recipe}'


class ShopingCart(models.Model):
    """Модель списка покупок пользователя."""
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='shoping_cart'
    )
    recipe = models.ForeignKey(
        'Recipe',
        null=True,
        on_delete=models.SET_NULL,
        related_name='shoping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoping'
            )
        ]

    def __str__(self) -> str:
        return f' У пользователя {self.user} в списке покупок {self.recipe}'


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientAmountRecipe(models.Model):
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE
        
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1),),
    )


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Таг'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        unique=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        unique=True,
        verbose_name='Слаг',
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


