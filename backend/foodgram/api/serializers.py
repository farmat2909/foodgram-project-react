import email
from rest_framework import serializers, validators

from recipes.models import Recipe, Tag, Ingredient, IngredientAmountRecipe
from users.models import User, Follow
from djoser.serializers import UserCreateSerializer


#python manage.py shell_plus --print-sql
#from api.serializers import *
#from users.models import *
#from recipes.models import *

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

#профиль пользователя
class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if Follow.objects.filter(user__username=user, following__username=obj.username).exists():
            return True
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, source='following.recipes', read_only=True)
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = Follow
        fields = ('user', 'following', 'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')


    def get_recipes_count(self, obj):
        return obj.following.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if Follow.objects.filter(user__username=user, following__username=obj.following.username).exists():
            return True
        return False

    def validate(self, data):
        user = data['user']
        author = data['following']
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписываться на себя.'
            )
        if Follow.objects.filter(user__username=user, following__username=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data





class UserCustomCreateSerializer(UserCreateSerializer):
    """Регистрация пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')



class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:

        model = IngredientAmountRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')





class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountRecipeSerializer(many=True, source='ingredientamountrecipe_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shoping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shoping_cart', 'name', 'image', 'text', 'cooking_time')


    def get_is_favorited(self, obj):
        author = self.context.get('request').user
        if author.is_anonymous:
            return None
        if obj.favorites.filter(user=author, pk=obj.pk).exists():
            return True
        return False


    def get_is_in_shoping_cart(self, obj):
        author = self.context.get('request').user
        if author.is_anonymous:
            return None
        if obj.shoping_cart.filter(user=author, pk=obj.pk).exists():
            return True
        return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
