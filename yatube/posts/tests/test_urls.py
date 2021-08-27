from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Name")
        cls.user_2 = User.objects.create_user(username="Name_1")
        cls.group = Group.objects.create(
            title="Название группы", slug="new_author",
        )
        cls.post = Post.objects.create(
            text="ж" * 100,
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_address_anonimus(self):
        """Доступность страниц для анонимного пользователя"""
        templates_url_names = (
            "/",
            f"/group/{self.group.slug}/",
            f"/{self.post.author}/",
            f"/{self.post.author}/{self.post.id}/",
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страницы по адресу /new/, /Name/1/, /Name/1/edit/,
        /Name/1/comment/, /Name/follow/, /Name/unfollow/ перенаправят
        анонимного пользователя на страницу логина."""
        templates_url_names = {
            "/new/":
            "/auth/login/?next=/new/",
            f"/{self.post.author}/{self.post.id}/comment/":
            f"/auth/login/?next=/{self.post.author}/{self.post.id}/comment/",
            f"/{self.post.author}/follow/":
            f"/auth/login/?next=/{self.post.author}/follow/",
            f"/{self.post.author}/unfollow/":
            f"/auth/login/?next=/{self.post.author}/unfollow/",
            f"/{self.post.author}/{self.post.id}/edit/":
            f"/auth/login/?next=/{self.post.author}/{self.post.id}/edit/",
        }
        for address, redirect_address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_edit_post_url_redirect_on_post(self):
        """Страница по адресу /Name/1/edit/ перенаправит
        не автора поста на страницу поста."""
        response = self.authorized_client_2.get(
            f"/{self.post.author}/{self.post.id}/edit/", follow=True
        )
        self.assertRedirects(response, (
            f"/{self.post.author}/{self.post.id}/comment/")
        )

    def test_follow_url_redirect_on_post(self):
        """Страницы по адресу /Name/follow/ и /Name/unfollow/ перенаправят
        на страницу автора при невозможности подписки/отписки."""
        templates_url_names = {
            f"/{self.user}/follow/": f"/{self.user}/",
            f"/{self.user}/unfollow/": f"/{self.user}/",
        }
        for address, redirect_address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_address_authorized(self):
        """Доступность страниц для авторизованного пользователя"""
        templates_url_names = (
            "/",
            f"/group/{self.group.slug}/",
            "/new/",
            "/follow/",
            f"/{self.post.author}/",
            f"/{self.post.author}/{self.post.id}/",
            f"/{self.post.author}/{self.post.id}/comment/",
            f"/{self.post.author}/{self.post.id}/edit/",
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "index.html": "/",
            "group.html": f"/group/{self.group.slug}/",
            "posts/follow.html": "/follow/",
            "posts/post_edit.html": (f"/{self.post.author}"
                                     f"/{self.post.id}/edit/"),
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Страница по адресу /admin/ne111/ возвращает страницу 404."""
        templates_url_names = (
            "/admin/ne111/",
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
