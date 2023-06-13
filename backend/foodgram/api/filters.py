import django_filters
from django.contrib.auth import get_user_model
from recipes.models import IngredientsModel, RecipesModel, TagsModel

UserModel = get_user_model()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = IngredientsModel
        fields = ('name', 'measurement_unit')


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=TagsModel.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=UserModel.objects.all())

    class Meta:
        model = RecipesModel
        fields = ('tags', 'author')
