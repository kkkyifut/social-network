from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username="Name")
        cls.post = Post.objects.create(
            text="ж" * 100,
            author=user,
        )

    def test_str_for_post(self):
        """Правильное отображение поля __str__ для Post."""
        post = PostModelTest.post
        expected_object_text = post.text[:15]
        self.assertEqual(expected_object_text, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название группы", slug="new_author",
        )

    def test_str_for_group(self):
        """Правильное отображение поля __str__ для Group."""
        group = GroupModelTest.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group))
