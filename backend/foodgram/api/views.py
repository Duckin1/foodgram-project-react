from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SmallRecipeSerializer, SubscriptionSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    serializer_class = SubscriptionSerializer

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'На себя нельзя подписаться / отписаться'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.filter(
            author=author, user=user)
        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'errors': 'Нельзя подписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'errors': 'Нельзя отписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [IngredientFilter, ]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add(self, model, pk, name):
        """Добавление рецепта в список пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relations = model.objects.filter(user=user, recipe=recipe)
        if relations.exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk, name):
        """Удаление рецепта из списка пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': f'Нельзя повторно удалить рецепт из {name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            url_name='favorite')
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов - Избранное."""
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            return self.add(Favorite, user, pk, name)
        if request.method == 'DELETE':
            name = 'избранного'
            return self.delete_relation(Favorite, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов - Список покупок."""
        user = request.user
        if request.method == 'POST':
            name = 'список покупок'
            return self.add(ShoppingCart, user, pk, name)
        if request.method == 'DELETE':
            name = 'списка покупок'
            return self.delete_relation(ShoppingCart, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['GET'], )
    def download_shopping_cart(self, request):
        if not request.user.cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientAmount.objects
            .filter(recipe__recipe_cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit'
            )
        )

        text = ''
        for ingredient in ingredients:
            text += '{} - {} {}. \n'.format(*ingredient)

        file = HttpResponse('Покупки:\n' + text, content_type='text/plain')

        file['Content-Disposition'] = 'attachment; filename=cart.txt'
        return file
