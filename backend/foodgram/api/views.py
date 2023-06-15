from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models import Follow
from recipes.models import (Favorite, IngredientsModel, RecipeIngredient,
                            RecipesModel, ShoppingCart, TagsModel)
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPagination
from .serializers import (ChangePasswordSerializer, FollowSerializer,
                          IngredientsSerializer, RecipeFollowSerializer,
                          RecipeGetSerializer, RecipesSerializer,
                          TagSerializer, UserLoginSerializer, UserSerializer)
from .utils import delete_obj, post_obj

UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)

    lookup_field = 'id'

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user

        if not check_password(
                serializer.validated_data['current_password'],
                current_user.password
        ):
            message = "Current Password is incorrect"
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        current_user.set_password(serializer.validated_data['new_password'])
        current_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Возможность получения Пользователя данных о себе

        GET запрос"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(UserModel, pk=kwargs.get('id'))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                UserModel, pk=self.kwargs.get('id')
            )
        )

    def delete(self, request, *args, **kwargs):
        follow = get_object_or_404(
            Follow,
            user=self.request.user,
            author=get_object_or_404(
                UserModel, pk=self.kwargs.get('id')
            )
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['id'] = int(self.kwargs.get('id'))
        return context


class UserLoginViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin,
):
    """Вьюсет логина"""
    permission_classes = (AllowAny,)

    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, )

        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get('password')
        email = serializer.validated_data.get('email')

        if not UserModel.objects.filter(email=email).exists():
            message = "This email has already been taken"
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(UserModel, email=email)
        if not check_password(password, user.password):
            message = "password is incorrect"
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        response = {
            "auth_token": str(token)
        }

        return Response(
            data=response,
            status=status.HTTP_201_CREATED
        )


class UserLogoutViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin,
):
    permission_classes = (IsAuthenticated,)

    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        Token.objects.filter(user_id=self.request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None

    queryset = TagsModel.objects.all()


class IngredientsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    permission_classes = (AllowAny,)
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None

    queryset = IngredientsModel.objects.all()


class RecipesViewSet(
    viewsets.ModelViewSet
):
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = RecipesModel.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response('Рецепт успешно удален',
                        status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipesSerializer

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited') or 0
        if int(is_favorited) == 1:
            return RecipesModel.objects.filter(
                favorites__user=self.request.user
            )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart') or 0
        if int(is_in_shopping_cart) == 1:
            return RecipesModel.objects.filter(
                cart__user=self.request.user
            )
        return RecipesModel.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('POST', 'DELETE'), )
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            return post_obj(request, pk, Favorite, RecipeFollowSerializer)
        return delete_obj(request, pk, Favorite)

    @action(detail=True, methods=('POST', 'DELETE'), )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return post_obj(request, pk, ShoppingCart, RecipeFollowSerializer)
        return delete_obj(request, pk, ShoppingCart)

    @action(detail=False, methods=('GET',), )
    def download_shopping_cart(self, request):
        if not request.user.cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(total=Sum('amount'))
        )
        shoping_cart = {}
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = f'{ingredient["total"]} {ingredient["ingredient__measurement_unit"]}'
            shoping_cart[name] = amount
        data = ''
        for key, value in shoping_cart.items():
            data += f'{key} - {value}\n'
        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class FollowListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
