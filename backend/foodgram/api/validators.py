from rest_framework.validators import ValidationError


def validate_time(value):
    """Валидация поля модели - время приготовления."""
    if value < 1:
        raise ValidationError(
            ['Время не может быть менее минуты.']
        )
