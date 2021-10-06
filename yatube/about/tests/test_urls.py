from http import HTTPStatus

from django.test import Client, TestCase


class AboutUrlsTest(TestCase):
    AUTHOR_URL = '/about/author/'
    TECH_URL = '/about/tech/'

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_available(self):
        """Проверить доступность страниц about."""
        url_to_check = (self.AUTHOR_URL, self.TECH_URL)
        for url in url_to_check:
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
