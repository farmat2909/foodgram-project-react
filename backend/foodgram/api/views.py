from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import Follow, User

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserCustomCreateSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=False, pagination_class=LimitOffsetPagination)
    def subscriptions(self, request):
        queryset = request.user.follower
        serializer = SubscribeSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        user = request.user.pk
        author = get_object_or_404(User, pk=id)
        serializer = SubscribeSerializer(data={'user': user, 'following': author.id}, context={'request': request})
        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            subscription = Follow.objects.filter(user=user, following=author)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'], serializer_class=FavoriteSerializer)
    def favorite(self, request, pk=None):
        user = request.user.id
        print(user)
        recipe = get_object_or_404(Recipe, pk=pk)
        print(recipe)
        serializer = FavoriteSerializer(data={'user': user, 'recipe': recipe.id}, context={'request': request})
        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)