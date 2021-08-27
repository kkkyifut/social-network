import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username="New Author")
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title="Название группы", slug="new_author",
            description="Описание"
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_data = {
            "author": self.user,
            "text": "ж" * 33,
            "group": self.group.id,
            "image": uploaded,
        }

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:new"),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.form_data["text"],
                group=self.group.id,
                image="posts/small.gif",
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post = Post.objects.create(
            author=self.user,
            text="Лошадь",
        )
        tasks_count = Post.objects.count()
        response = self.authorized_client.post(reverse(
            "posts:edit",
            kwargs={"username": self.user.username, "post_id": post.id}),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "posts:post",
            kwargs={"username": self.user.username, "post_id": post.id})
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.form_data["text"],
            ).exists()
        )


class FollowFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username="New Author_1")
        cls.user_2 = User.objects.create_user(username="New Author_2")

    def test_follow(self):
        """Валидная форма подписывает и отписывает пользователя."""
        Follow.objects.get_or_create(author=self.user_1, user=self.user_2)
        self.assertTrue(
            Follow.objects.filter(
                author=self.user_1, user=self.user_2
            ).exists()
        )
        follow = Follow.objects.filter(author=self.user_1, user=self.user_2)
        follow.delete()
        self.assertFalse(
            Follow.objects.filter(
                author=self.user_1, user=self.user_2
            ).exists()
        )
