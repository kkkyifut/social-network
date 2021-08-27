from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемые при помощи имён
        about:author и about:tech, доступны."""
        templates_url_names = (
            "about:author",
            "about:tech",
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к статичным страницам about
        применяются соответствующие шаблоны about
        (author/tech.html)."""
        templates_pages_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
