from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShopingCart, Tag
from users.models import Follow, User

from .filters import RecipeFilter
from .permissions import AuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShopingCartSerializer, SubscribeSerializer,
                          TagSerializer)
from .utils import download_shopping_cart


class CustomUserViewSet(UserViewSet):
    """Создание пользователя и подписки."""
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrAdminOrReadOnly,)

    @action(detail=False, pagination_class=LimitOffsetPagination)
    def subscriptions(self, request):
        queryset = request.user.follower
        context = {'request': request}
        serializer = SubscribeSerializer(
            queryset, context=context, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        user = request.user.pk
        author = get_object_or_404(User, pk=id)
        data = {'user': user, 'following': author.id}
        context = {'request': request}
        serializer = SubscribeSerializer(data=data, context=context)
        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            subscription = Follow.objects.filter(
                user=user, following=author)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Создание и получение рецепта.
    Добавление в избранное, удаление.
    Добавление в список покупок, удаление и скачивание списка."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=FavoriteSerializer)
    def favorite(self, request, pk=None):
        return self._logic_favorite_shopping_cart(
            request, pk, Recipe, Favorite, FavoriteSerializer)

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=ShopingCartSerializer)
    def shopping_cart(self, request, pk=None):
        return self.__logic_favorite_shopping_cart(
            request, pk, Recipe, ShopingCart, ShopingCartSerializer)

    @action(detail=False)
    def download_shopping_cart(self, request):
        return download_shopping_cart(request)

    def _logic_favorite_shopping_cart(self, request, recipe_id, model_recipe, model, serializer):
        user = request.user.id
        recipe = get_object_or_404(model_recipe, pk=recipe_id)
        data = {'user': user, 'recipe': recipe.id}
        context = {'request': request}
        serializer = serializer(data=data, context=context)
        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            favorite = model.objects.filter(user=user, recipe=recipe)
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
