from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

User = get_user_model()


class Group(models.Model):
    """Модель для группы."""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(
        'Описание',
        validators=[MaxLengthValidator(500, message='Превышена длина')])

    class Meta:
        db_table = 'group'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для поста."""
    text = models.TextField(
        'Текст',
        validators=[MaxLengthValidator(3000, message='Превышена длина')])
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='группа',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True, )

    class Meta:
        db_table = 'post'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='пост'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='автор')
    text = models.TextField(
        'Текст комментария',
        validators=[MaxLengthValidator(500)])
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Модель для записи подписок."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='подписчик')
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='автор')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'),
            CheckConstraint(check=~Q(user=F('author')), name='self_following')
        ]
