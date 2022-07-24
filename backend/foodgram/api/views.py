from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from .serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, UserCustomCreateSerializer, SubscribeSerializer
from recipes.models import Tag, Recipe, Ingredient
from users.models import User, Follow


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