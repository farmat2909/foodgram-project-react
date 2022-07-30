from posixpath import basename

from django.urls import include, path, re_path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
