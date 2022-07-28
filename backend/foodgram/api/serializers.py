import base64
from rest_framework import serializers, validators

from drf_base64.fields import Base64ImageField
from recipes.models import Recipe, Tag, Ingredient, IngredientAmountRecipe
from users.models import User, Follow
from djoser.serializers import UserCreateSerializer


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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')


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


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientAmountRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
        if obj.favorites.filter(user=author, recipe=obj.pk).exists():
            return True
        return False


    def get_is_in_shoping_cart(self, obj):
        author = self.context.get('request').user
        if author.is_anonymous:
            return None
        if obj.shoping_cart.filter(user=author, pk=obj.pk).exists():
            return True
        return False


class IngredientWriteSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(write_only=True)
    id = serializers.PrimaryKeyRelatedField(source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmountRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание рецепта."""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientWriteSerializer(many=True, required=True)
    image = Base64ImageField(required=True)


    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients', 'name', 'image', 'text', 'cooking_time')


    def validate(self, data):
        return data


    def create(self, validated_data):
        print(validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for elem in ingredients:
            IngredientAmountRecipe.objects.create(recipe=recipe, **elem)
        return recipe


    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
