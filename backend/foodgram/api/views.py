from django.shortcuts import render
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe

# Create your views here.

UserModel = get_user_model()

class UserViewSet():
    #pagination_class = PageLimitPagination
    pass


class IngredientViewSet():
    pass


class RecipeViewSet():
    pass


class TagViewSet():
    pass


