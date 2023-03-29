from rest_framework import serializers

from recipes.models import Ingredients, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        mo