import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Name")
        cls.user_1 = User.objects.create_user(username="Name_1")
        cls.user_2 = User.objects.create_user(username="Name_2")
        cls.group = Group.objects.create(
            title="Название группы", slug="new_author",
            description="Описание"
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
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
        self.post = Post.objects.create(
            author=self.user,
            text="ж" * 50,
            group=self.group,
            image=uploaded,
        )

    def pages_show_correct_context(self, new_object_1, new_object_2):
        profile_username = new_object_1.username
        profile_post = new_object_2.text
        profile_pub_date = new_object_2.pub_date
        profile_image = new_object_2.image
        self.assertEqual(profile_username, self.user.username)
        self.assertEqual(profile_post, self.post.text)
        self.assertEqual(profile_pub_date, self.post.pub_date)
        self.assertEqual(profile_image, self.post.image)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            "index.html": reverse("posts:index"),
            "group.html": reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ),
            "posts/post_edit.html": reverse("posts:new"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        response_context_page = response.context["page"][0]
        form_field_text = response_context_page.text
        form_field_date = response_context_page.pub_date
        form_field_author = response_context_page.author
        form_field_group = response_context_page.group
        form_field_image = response_context_page.image
        self.assertEqual(form_field_text, self.post.text)
        self.assertEqual(form_field_date, self.post.pub_date)
        self.assertEqual(form_field_author, self.post.author)
        self.assertEqual(form_field_group, self.post.group)
        self.assertEqual(form_field_image, self.post.image)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        first_object = response.context["page"][0].group
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_description_0 = first_object.description
        second_object = response.context["page"][0].image
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_description_0, self.group.description)
        self.assertEqual(second_object, self.post.image)

    def test_post_on_the_group_shows_on_correct_page(self):
        """Пост с указанной группой появляется на
        главной странице и на странице группы."""
        response_index = self.authorized_client.get(reverse("posts:index"))
        response_group = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        first_object = response_index.context["page"][0].group
        second_object = response_group.context["page"][0].group
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(second_object.title, self.group.title)

    def test_post_on_the_group_dont_shows_on_uncorrect_page(self):
        """Пост с указанной группой не
        появляется на странице другой группы."""
        group_another = Group.objects.create(
            title="Название группы Another", slug="new_author_another",
            description="Описание группы Another"
        )
        Post.objects.create(
            text="ййй",
            author=self.user,
            group=group_another,
        )
        response = self.authorized_client.get(reverse(
            "posts:group_posts",
            kwargs={"slug": self.group.slug})
        )
        response_another = self.authorized_client.get(reverse(
            "posts:group_posts",
            kwargs={"slug": group_another.slug})
        )
        first_object = response.context["page"][0].group
        second_object = response_another.context["page"][0].group
        self.assertNotEqual(first_object.slug, second_object.slug)

    def test_post_of_the_follow_shows_on_correct_page(self):
        """Пост избранного автора появляется
        на странице с избранными авторами."""
        post_1 = Post.objects.create(
            text="ййй",
            author=self.user_1,
        )
        Follow.objects.get_or_create(
            author=self.user, user=self.user_1
        )
        Follow.objects.get_or_create(
            author=self.user_1, user=self.user_2
        )
        response_follow_1 = self.authorized_client_1.get(reverse(
            "posts:follow_index")
        )
        response_follow_2 = self.authorized_client_2.get(reverse(
            "posts:follow_index")
        )
        text_follow_1 = response_follow_1.context["page"][0].text
        text_follow_2 = response_follow_2.context["page"][0].text
        self.assertEqual(text_follow_1, self.post.text)
        self.assertEqual(text_follow_2, post_1.text)

    def test_new_post_pages_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:new"))
        new_object = response.context["post"]
        new_post_text = new_object.text
        new_post_group = new_object.group
        self.assertEqual(new_post_text, "")
        self.assertEqual(new_post_group, None)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:edit",
            kwargs={"username": self.user.username, "post_id": self.post.id}))
        new_object_1 = response.context["author"]
        new_object_2 = response.context["post"]
        self.pages_show_correct_context(
            new_object_1, new_object_2
        )

    def test_username_post_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:post",
            kwargs={"username": self.user.username, "post_id": self.post.id})
        )
        new_object_1 = response.context["author"]
        new_object_2 = response.context["post"]
        self.pages_show_correct_context(
            new_object_1, new_object_2
        )

    def test_username_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:profile", kwargs={"username": self.user.username})
        )
        new_object_1 = response.context["author"]
        new_object_2 = response.context["page"][0]
        self.pages_show_correct_context(
            new_object_1, new_object_2
        )

    def test_follow_on_user(self):
        """Подписка на автора работает корректно."""
        self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": self.user_1.username}
        ))
        following = Follow.objects.filter(
            author=self.user_1, user=self.user
        ).exists()
        self.assertTrue(following)
        for _ in range(3):
            self.authorized_client.get(reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_1.username}
            ))
        follow_count = Follow.objects.all().count()
        self.assertEqual(follow_count, 1)

    def test_unfollow_on_user(self):
        """Отписка от автора работает корректно."""
        following = Follow.objects.get_or_create(
            author=self.user_1, user=self.user
        )
        self.assertTrue(following)
        self.authorized_client.get(reverse(
            "posts:profile_unfollow",
            kwargs={"username": self.user_1.username}
        ))
        following = Follow.objects.filter(
            author=self.user_1, user=self.user
        ).exists()
        self.assertFalse(following)


class PaginatorViewsTest(TestCase):
    """Тестирование пагинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Name_1")
        object_list = []
        cls.group = Group.objects.create(
            title="Название группы 1", slug="new_author_1",
            description="Описание 1"
        )
        for _ in range(13):
            cls.post = Post.objects.create(
                text="ж" * 100,
                author=cls.user,
                group=cls.group,
            )
            object_list.append(cls.post)

    def setUp(self):
        self.client = Client()

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)

    def test_first_page_group_contains_twelve_records(self):
        response = self.client.get(reverse(
            "posts:group_posts",
            kwargs={"slug": self.group.slug})
        )
        self.assertEqual(len(response.context.get("page").object_list), 12)

    def test_second_page_group_contains_one_record(self):
        response = self.client.get(reverse(
            "posts:group_posts",
            kwargs={"slug": self.group.slug}) + "?page=2"
        )
        self.assertEqual(len(response.context.get("page").object_list), 1)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            "posts:profile",
            kwargs={"username": self.user.username})
        )
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_profile_contains_three_records(self):
        response = self.client.get(reverse(
            "posts:profile",
            kwargs={"username": self.user.username}) + "?page=2"
        )
        self.assertEqual(len(response.context.get("page").object_list), 3)
