from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import IngredientAmountRecipe


def download_shopping_cart(request):
    """
    Загрузка списка покупок.
    """
    ingredients = IngredientAmountRecipe.objects.filter(
        recipe__shoping_cart__user=request.user).values(
        'ingredient__name',
        'ingredient__measurement_unit').annotate(total=Sum('amount'))
    shopping_list = 'Список покупок:\n\n'
    for number, ingredient in enumerate(ingredients, start=1):
        shopping_list += (
            f'{ingredient["ingredient__name"]}: '
            f'{ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n')
    cart = 'shopping-list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = (f'attachment;'
                                       f'filename={cart}')
    return response
