from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets
from recipes.models import Tag, Ingredient, Recipe
from .serializers import SubscriptionSerializer
from users.models import Subscription
from rest_framework.permissions import IsAuthenticated


UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов на которых подписан пользователь."""
        user = request.UserModel
        queryset = user.follower.all()
        pages = self.paginate_queryser(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, contex={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
             url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписки на автора."""
        user = request.UserModel
        author = get_object_or_404(UserModel, id=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться и отписаться от себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = Subscriptions.objects.filter(
            author=author, user=user
        )
        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'errors': 'Нельзя подписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = Subscriptions.objects.create(author=author, user=user)
            serializer = SubscriptionsSerializer(
                queryset, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'errors': 'Нельзя отписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
