from django.db.models import IntegerField, Value
from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, Ingredient


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in start_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class RecipeFilter(filters.FilterSet):
    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.CharFilter(lookup_expr='exact')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='filter'
    )

    def filter(self, queryset, name, value):
        if name == 'is_in_shopping_cart' and value:
            queryset = queryset.filter(
                shopping_cart__user=self.request.user
            )
        if name == 'is_favorited' and value:
            queryset = queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']
