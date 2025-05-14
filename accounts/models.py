from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('seller', 'Продавец'),
        ('buyer', 'Покупатель'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    # Переопределяем поле groups с уникальным related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='Группы',
        blank=True,
        help_text=(
            'Группы, к которым относится пользователь. '
            'Пользователь получит все разрешения своих групп.'
        ),
        related_name='accounts_user_groups',      # <- уникальное имя
        related_query_name='account_user',
    )

    # Переопределяем поле user_permissions с уникальным related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='Разрешения пользователя',
        blank=True,
        help_text='Конкретные разрешения для этого пользователя.',
        related_name='accounts_user_permissions', # <- уникальное имя
        related_query_name='account_user_perm',
    )

    def is_seller(self):
        return self.role == 'seller'

    def is_buyer(self):
        return self.role == 'buyer'

    def is_admin(self):
        return self.role == 'admin'

