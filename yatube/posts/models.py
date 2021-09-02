from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для групп."""

    title = models.CharField(
        max_length=200, verbose_name="Название",
        help_text="Введите название группы"
    )
    slug = models.SlugField(
        max_length=100, unique=True, allow_unicode=True,
        verbose_name="Ссылка", help_text="Введите уникальное значение"
    )
    description = models.TextField(
        verbose_name="Описание", blank=True, help_text="необязательно"
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Модель для постов."""

    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="author_posts", verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="group_posts", verbose_name="Группа"
    )
    image = models.ImageField(
        upload_to="posts/", blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return self.text[:15]


class Message(models.Model):
    """Модель для сообщений."""

    text = models.TextField(verbose_name="Текст сообщения")
    dispatched = models.DateTimeField(
        "sending_date", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="author_messages", verbose_name="Отправитель"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="user_messages", verbose_name="Получатель"
    )
    image = models.ImageField(
        upload_to="posts/", blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        ordering = ("-dispatched",)

    def __str__(self) -> str:
        return self.text[:200]


class Comment(models.Model):
    """Модель для комментариев."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Пост"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст")
    created = models.DateTimeField("date created", auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        return self.text[:50]


class Follow(models.Model):
    """Модель для подписок на авторов."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower", verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following", verbose_name="Автор"
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=("user", "author"),
            name="unique_list"
        )]
