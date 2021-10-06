from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTest(TestCase):

    ABOUT_AUTHOR = 'about:author'
    ABOUT_TECH = 'about:tech'

    AUTHOR_TEMPLATE = 'author.html'
    TECH_TEMPLATE = 'tech.html'

    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """Страницы about доступны по имени"""
        pages_names = (
            self.ABOUT_AUTHOR, self.ABOUT_TECH,
        )
        for name in pages_names:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_pages_use_correct_template(self):
        """Страницы about используют правильный шаблон"""
        name_template = {
            self.ABOUT_AUTHOR: self.AUTHOR_TEMPLATE,
            self.ABOUT_TECH: self.TECH_TEMPLATE,
        }
        for name, template in name_template.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
