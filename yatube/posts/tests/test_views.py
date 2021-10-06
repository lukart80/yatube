import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User


class PostPagesTest(TestCase):
    HOMEPAGE_URL = '/'
    CREATE_POST_URL = '/new/'
    CREATE_POST_REDIRECT_URL = '/auth/login/?next=/new/'

    INDEX_NAME = 'index'
    GROUP_NAME = 'group'
    NEW_POST_NAME = 'new_post'
    FOLLOW_INDEX_NAME = 'follow_index'
    PROFILE_FOLLOW_NAME = 'profile_follow'
    PROFILE_UNFOLLOW_NAME = 'profile_unfollow'

    INDEX_TEMPLATE = 'index.html'
    GROUP_TEMPLATE = 'group.html'
    NEW_POST_TEMPLATE = 'new_post.html'
    FOLLOW_INDEX_TEMPLATE = 'follow.html'

    USERNAME = 'test_user'
    SAMPLE_TEXT = 'test'
    SAMPLE_TEXT2 = 'another-test'
    POST_TEXT = 'Это текст поста для теста'
    USERNAME1 = 'test_user1'
    USERNAME2 = 'test_user2'
    CACHE_POST = 'post to test cache'
    COMMENT_TEXT = 'text of the comment'

    PAGE_VAR = 'page'
    POST_VAR = 'post'
    FORM_VAR = 'form'

    GROUP_ATTR = 'group'
    TEXT_ATTR = 'text'
    AUTHOR_ATTR = 'author'
    IMAGE_ATTR = 'image'

    GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
           b'\x01\x00\x80\x00\x00\x00\x00\x00'
           b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
           b'\x00\x00\x00\x2C\x00\x00\x00\x00'
           b'\x02\x00\x01\x00\x00\x02\x02\x0C'
           b'\x0A\x00\x3B')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=cls.SAMPLE_TEXT,
            description=cls.SAMPLE_TEXT,
            slug=cls.SAMPLE_TEXT
        )
        cls.group2 = Group.objects.create(
            title=cls.SAMPLE_TEXT2,
            description=cls.SAMPLE_TEXT2,
            slug=cls.SAMPLE_TEXT2
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):

        self.user = User.objects.create_user(username=self.USERNAME)
        self.user1 = User.objects.create_user(username=self.USERNAME1)
        self.user2 = User.objects.create_user(username=self.USERNAME2)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.GIF,
            content_type='image/gif'
        )

        self.post = Post.objects.create(
            text=self.POST_TEXT,
            author=self.user,
            group=PostPagesTest.group,
            image=self.uploaded,
        )
        self.post2 = Post.objects.create(
            text=self.POST_TEXT,
            author=self.user,
            group=PostPagesTest.group,
        )
        self.user_id = self.user.pk
        self.group_url = f'/group/{self.group.slug}/'
        self.profile_url = f'/{self.user.username}/'
        self.post_url = f'/{self.user.username}/{self.post.pk}/'
        self.post2_url = f'/{self.user.username}/{self.post2.pk}/'

        self.post_edit_url = f'/{self.user.username}/{self.post.pk}/edit/'

        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_correct_template_used_by_name(self):
        """Используются нужные шаблоны при обращении по имени."""
        templates_names = {
            self.INDEX_TEMPLATE: reverse(self.INDEX_NAME),
            self.GROUP_TEMPLATE: reverse(
                self.GROUP_NAME,
                args=[self.group.slug]),
            self.NEW_POST_TEMPLATE: reverse(self.NEW_POST_NAME),
            self.FOLLOW_INDEX_TEMPLATE: reverse(self.FOLLOW_INDEX_NAME),

        }

        for template, name in templates_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_post_context(self):
        """Проверка отображения поста на разных страницах."""
        urls_context_var = {
            self.HOMEPAGE_URL: self.PAGE_VAR,
            self.group_url: self.PAGE_VAR,
            self.profile_url: self.PAGE_VAR,
            self.post_url: self.POST_VAR,
        }
        attribute_expected = {
            self.TEXT_ATTR: self.POST_TEXT,
            self.AUTHOR_ATTR: self.user,
            self.GROUP_ATTR: self.group,
            self.IMAGE_ATTR: None,
        }
        for url, context_var in urls_context_var.items():
            response = self.authorized_client.get(url)
            if context_var == self.POST_VAR:
                context_object = response.context[context_var]
            else:
                context_object = response.context[context_var][0]
            for attribute, expected in attribute_expected.items():
                with self.subTest(attribute=attribute, url=url):
                    if attribute == self.IMAGE_ATTR:
                        self.assertContains(response, '<img')
                    else:
                        self.assertEqual(
                            getattr(context_object, attribute), expected)

    def test_post_create_edit_context(self):
        """Проверить контекст страниц для создания и редактирования поста."""
        urls_to_test = (
            self.CREATE_POST_URL,
            self.post_edit_url,
        )
        form_fields = {
            self.TEXT_ATTR: forms.fields.CharField,
            self.GROUP_ATTR: forms.models.ModelChoiceField,
        }
        for url in urls_to_test:
            response = self.authorized_client.get(url)
            post_form = response.context.get(self.FORM_VAR)

            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    self.assertIsInstance(post_form.fields[value], expected)

    def test_other_group_does_not_contain_post(self):
        """Проверить, что поста нет в другой группе."""
        response = self.authorized_client.get(
            reverse(self.GROUP_NAME, args=[self.SAMPLE_TEXT2]))
        self.assertNotContains(response, self.POST_TEXT)

    def test_comment_form_appears_on_post_page(self):
        """Проверить, что форма для комментариев появляется на странице с
        постом для авторизованного пользователя. """
        response = self.authorized_client.get(
            self.post_url
        )
        form = response.context.get(self.FORM_VAR)
        form_fields = {
            self.TEXT_ATTR: forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields[value], expected)

    def test_comment_appears_on_post_page(self):
        """Проверить, что комментарий появляется на странице с постом."""
        Comment.objects.create(
            post=self.post,
            author=self.user,
            text=self.COMMENT_TEXT,
        )
        response = self.authorized_client.get(self.post_url)
        self.assertContains(response, self.COMMENT_TEXT)
        response2 = self.authorized_client.get(self.post2_url)
        self.assertNotContains(response2, self.COMMENT_TEXT)

    def test_authenticated_user_can_follow(self):
        """Проверяем, что авторизованный пользователь может подписаться."""
        self.assertFalse(Follow.objects.filter(user=self.user1,
                                               author=self.user).exists())

        response = self.authorized_client1.get(
            reverse(self.PROFILE_FOLLOW_NAME, args=[self.user.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.filter(user=self.user1,
                                              author=self.user).exists())

    def test_authenticated_user_can_unfollow(self):
        """Проверяем, что авторизованный пользователь может отписаться."""
        response = self.authorized_client1.get(
            reverse(self.PROFILE_FOLLOW_NAME, args=[self.user.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.filter(user=self.user1,
                                              author=self.user).exists())

        response = self.authorized_client1.get(
            reverse(self.PROFILE_UNFOLLOW_NAME, args=[self.user.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Follow.objects.filter(user=self.user1,
                                               author=self.user).exists())

    def test_user_cannot_follow_himself(self):
        """Проверить, что пользователь не может подписаться сам на себя."""
        self.assertFalse(Follow.objects.exists())
        self.authorized_client.get(
            reverse(self.PROFILE_FOLLOW_NAME, args=[self.user.username])
        )
        self.assertFalse(Follow.objects.exists())

    def test_users_feed(self):
        """Провереям, что посты из подписок появляются в ленте пользователя."""

        response = self.authorized_client1.get(
            reverse(self.FOLLOW_INDEX_NAME)
        )
        page = response.context.get(self.PAGE_VAR)
        self.assertEqual(len(page), 0)

        self.authorized_client1.get(
            reverse(self.PROFILE_FOLLOW_NAME, args=[self.user.username]))
        response = self.authorized_client1.get(
            reverse(self.FOLLOW_INDEX_NAME)
        )
        page = response.context.get(self.PAGE_VAR)
        self.assertEqual(len(page), self.user.posts.count())
        for post in page:
            self.assertTrue(post.author == self.user)

        response = self.authorized_client2.get(
            reverse(self.FOLLOW_INDEX_NAME)
        )
        page = response.context.get(self.PAGE_VAR)
        self.assertEqual(len(page), 0)

    def test_cache(self):
        """Проверка кэширования главной страницы."""
        self.authorized_client.get(reverse(self.INDEX_NAME))
        Post.objects.create(
            text=self.CACHE_POST,
            author=self.user,
        )
        response = self.authorized_client.get(reverse(self.INDEX_NAME))
        self.assertNotContains(response, self.CACHE_POST)
        cache.clear()
        response = self.authorized_client.get(reverse(self.INDEX_NAME))
        self.assertContains(response, self.CACHE_POST)


class PaginatorViewsTest(TestCase):
    SECOND_PAGE = '?page=2'
    INDEX_NAME = 'index'
    GROUP_NAME = 'group'
    PROFILE_NAME = 'profile'

    SAMPLE_TEXT = 'test'
    USERNAME = 'test_user'

    PAGE_VAR = 'page'

    def setUp(self):
        self.user = User.objects.create_user(username=self.USERNAME)
        self.guest_client = Client()
        self.group = Group.objects.create(
            title=self.SAMPLE_TEXT,
            description=self.SAMPLE_TEXT,
            slug=self.SAMPLE_TEXT,
        )
        obj = list(Post(
            text=self.SAMPLE_TEXT,
            author=self.user,
            group=self.group) for _ in range(13))
        Post.objects.bulk_create(obj)
        cache.clear()

    def test_paginated_pages(self):
        """Проверить страницы с паджинатором."""
        url_value = {
            reverse(self.INDEX_NAME): 10,
            reverse(self.INDEX_NAME) + self.SECOND_PAGE: 3,
            reverse(self.GROUP_NAME, args=[self.group.slug]): 10,
            reverse(self.GROUP_NAME,
                    args=[self.group.slug]) + self.SECOND_PAGE: 3,
            reverse(self.PROFILE_NAME, args=[self.USERNAME]): 10,
            reverse(self.PROFILE_NAME,
                    args=[self.USERNAME]) + self.SECOND_PAGE: 3
        }

        for url, value in url_value.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context[self.PAGE_VAR].object_list), value)
