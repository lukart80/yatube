from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostUrlsTest(TestCase):

    HOMEPAGE_URL = '/'
    CREATE_POST_URL = '/new/'
    CREATE_POST_REDIRECT_URL = '/auth/login/?next=/new/'
    BAD_URL = '/afaf/afaf/afaf/'
    FOLLOW_INDEX_URL = '/follow/'
    FOLLOW_INDEX_REDIRECT_URL = '/auth/login/?next=/follow/'

    INDEX_TEMPLATE = 'index.html'
    GROUP_TEMPLATE = 'group.html'
    NEW_POST_TEMPLATE = 'new_post.html'
    FOLLOW_INDEX_TEMPLATE = 'follow.html'

    USERNAME = 'test_user'
    ANOTHER_USERNAME = 'another_user'
    SAMPLE_TEXT = 'test'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=cls.SAMPLE_TEXT,
            description=cls.SAMPLE_TEXT,
            slug=cls.SAMPLE_TEXT
        )
        cls.group_url = f'/group/{cls.group.slug}/'

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=self.USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text=self.SAMPLE_TEXT,
            group=PostUrlsTest.group,
            author=self.user
        )
        self.post_id = self.post.pk
        self.username = self.user.username
        self.another_user = User.objects.create_user(
            username=self.ANOTHER_USERNAME)
        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(self.another_user)

        self.profile_url = f'/{self.username}/'
        self.post_url = f'/{self.username}/{self.post_id}/'
        self.post_edit_url = f'/{self.username}/{self.post_id}/edit/'
        self.post_edit_redirect_url = (f'/auth/login/?next=/{self.username}/'
                                       f'{self.post_id}/edit/')
        self.follow_url = f'/{self.username}/follow/'
        self.follow_url_redirect = (f'/auth/login/?next='
                                    f'/{self.username}/follow/')
        self.unfollow_url = f'/{self.username}/unfollow/'
        self.unfollow_url_redirect = (f'/auth/login/?next='
                                      f'/{self.username}/unfollow/')

        cache.clear()

    def test_urls_status_codes_for_anonymous_user(self):
        """Тест URL для анонимного пользователя."""
        url_names = {
            self.HOMEPAGE_URL: HTTPStatus.OK,
            PostUrlsTest.group_url: HTTPStatus.OK,
            self.CREATE_POST_URL: HTTPStatus.FOUND,
            self.profile_url: HTTPStatus.OK,
            self.post_url: HTTPStatus.OK,
            self.post_edit_url: HTTPStatus.FOUND,
            self.FOLLOW_INDEX_URL: HTTPStatus.FOUND,
            self.follow_url: HTTPStatus.FOUND,
            self.unfollow_url: HTTPStatus.FOUND,
        }

        for address, status_code in url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_anonymous_user_url_redirect(self):
        """Анонимный пользователь будет перенаправлен на страницу логина."""
        url_redirect = {
            self.CREATE_POST_URL: self.CREATE_POST_REDIRECT_URL,
            self.post_edit_url: self.post_edit_redirect_url,
            self.FOLLOW_INDEX_URL: self.FOLLOW_INDEX_REDIRECT_URL,
            self.follow_url: self.follow_url_redirect,
            self.unfollow_url: self.unfollow_url_redirect,
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_urls_status_codes_for_authorized_user(self):
        """Проверка url для авторизованного пользователя."""
        url_code = {
            self.CREATE_POST_URL: HTTPStatus.OK,
            self.post_edit_url: HTTPStatus.OK,
        }
        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_another_user_cannot_edit_post(self):
        """Не автор поста не может его редактировать."""
        response = self.other_authorized_client.get(
            self.post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.post_url)

    def test_urls_use_correct_templates(self):
        """Страницы используют правильные шаблоны."""

        templates_urls_names = {
            self.HOMEPAGE_URL: self.INDEX_TEMPLATE,
            self.group_url: self.GROUP_TEMPLATE,
            self.CREATE_POST_URL: self.NEW_POST_TEMPLATE,
            self.post_edit_url: self.NEW_POST_TEMPLATE,
            self.FOLLOW_INDEX_URL: self.FOLLOW_INDEX_TEMPLATE,

        }

        for url, template in templates_urls_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
