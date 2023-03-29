from django.core.validators import RegexValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Можно использовать только латинские буквы и символы',
            ),
        ]
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name

class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name

class Recipes(models.Model):
    tags = models.ManyToManyField(Tag, )
