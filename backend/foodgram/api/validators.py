from rest_framework.validators import ValidationError


def validate_time(value):
    """Валидация поля модели - время приготовления."""
    if value < 1:
        raise ValidationError(
            ['Время не может быть менее минуты.']
        )


def validate_ingredients(data):
    """Валидация ингредиентов и количества."""
    if not data:
        raise ValidationError({'ingredients': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'ingredients': ['Не переданы ингредиенты.']})
    unique_ingredient = []
    for ingredient in data:
        if not ingredient.get('id'):
            raise ValidationError(
                {'ingredients': ['Отсутствует id ингредиаента.']})
        id = ingredient.get('id')
        if not Ingredient.objects.filter(id=id).exists():
            raise ValidationError(
                {'ingredients': ['Нельзя дублировать имена ингредиентов.']}
            )
        unique_ingredient.append(id)
        amount = int(ingredient.get('amount'))
        if amount < 1:
            raise ValidationError(
                {'amount': ['Количество не может быть менее 1.']})
    return data


def validate_tags(data):
    if not data:
        raise ValidationError({'tags': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'tags': ['Необходимо выбрать хотя бы 1 тэг.']})
    for tag in data:
        if not Tag.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Данный тэг отсутствует в БД.']})
    return data
