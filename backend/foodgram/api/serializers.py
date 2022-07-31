from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers, validators

from recipes.models import (Favorite, Ingredient, IngredientAmountRecipe,
                            Recipe, ShopingCart, Tag)
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта базовый."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Follow.objects.filter(
                                user__username=user,
                                following__username=obj.username).exists()


class UserCustomCreateSerializer(UserCreateSerializer):
    """Регистрация пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели ингредиентов."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmountRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов для записи рецепта."""
    amount = serializers.IntegerField(write_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmountRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта на чтение."""
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountRecipeSerializer(
        many=True,
        source='ingredientamountrecipe_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        author = self.context.get('request').user
        if author.is_anonymous:
            return None
        return obj.favorites.filter(user=author, recipe=obj.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        author = self.context.get('request').user
        if author.is_anonymous:
            return None
        return obj.shopping_cart.filter(user=author, pk=obj.pk).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание рецепта."""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientWriteSerializer(many=True, required=True)
    image = Base64ImageField(required=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        tags = data['tags']
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты должны присутствовать в рецепте.'
            )
        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                'Необходимо указать тег.'
            )
        if data['cooking_time'] < 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть положильным числом.'
            )
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        ingredients_data = []
        for key in ingredients:
            if key in ingredients_data:
                raise serializers.ValidationError(
                    'Ингредиент не может повторяться!'
                )
            ingredients_data.append(key)
        return data

    def ingredient_get_or_create(self, obj, data):
        new_ingredients = []
        for elem in data:
            data, status = (
                IngredientAmountRecipe.objects.get_or_create(
                    recipe=obj, **elem)
            )
            new_ingredients.append(data)
        return new_ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientAmountRecipe.objects.bulk_create(
            [IngredientAmountRecipe(
                recipe=recipe,
                ingredient=elem.get('ingredient'),
                amount=elem.get('amount')) for elem in ingredients]
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients = instance.ingredientamountrecipe_set
        instance.ingredients.clear()
        new_ingredients = self.ingredient_get_or_create(
            instance, ingredients_data)
        ingredients.set(new_ingredients)
        instance.tags.set(tags_data)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    user = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all()
    )
    following = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all()
    )
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(
        many=True,
        source='following.recipes',
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'user',
            'following',
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Follow.objects.filter(
                user__username=user,
                following__username=obj.following.username).exists()

    def validate(self, data):
        user = data['user']
        author = data['following']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписываться на себя.'
            )
        if Follow.objects.filter(
                user__username=user, following__username=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер избранного."""
    user = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Recipe.objects.all()
    )
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(
                user__username=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в избранном.'
            )
        return data


class ShopingCartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в список покупок."""
    user = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Recipe.objects.all())
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShopingCart
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShopingCart.objects.filter(
                user__username=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке покупок.'
            )
        return data
