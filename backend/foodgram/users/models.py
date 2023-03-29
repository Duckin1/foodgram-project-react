from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import DateTimeField, UniqueConstraint, CheckConstraint, Q, F


class User(AbstractUser):
    """Класс пользователя."""
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
    )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='following',
    )
    follow_date = DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='\nRepeat subscription\n',
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='\nNo self sibscription\n'
            )
        )

        def __str__(self) -> str:
            return f'{self.user.username} -> {self.author.username}'
