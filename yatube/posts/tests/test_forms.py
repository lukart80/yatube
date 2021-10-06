import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Post, User


class FormTest(TestCase):
    HOMEPAGE_URL = '/'
    POST_CREATE_URL_NAME = 'new_post'

    USER_NAME = 'test_user'
    SAMPLE_TEXT = 'Тест пост'
    EDIT_TEXT = 'Измененный текст'

    GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
           b'\x01\x00\x80\x00\x00\x00\x00\x00'
           b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
           b'\x00\x00\x00\x2C\x00\x00\x00\x00'
           b'\x02\x00\x01\x00\x00\x02\x02\x0C'
           b'\x0A\x00\x3B')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):
        self.user = User.objects.create_user(username=self.USER_NAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_edit = Post.objects.create(
            text=self.SAMPLE_TEXT,
            author=self.user
        )
        self.post_edit_url = f'/{self.user.username}/{self.post_edit.id}/edit/'
        self.upload = SimpleUploadedFile(
            name='small.gif',
            content=self.GIF,
            content_type='image/gif'
        )
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_post_form(self):
        """Проверка формы для создания поста."""
        form_data = {
            'text': self.SAMPLE_TEXT,
            'image': self.upload
        }
        response = self.authorized_client.post(
            reverse(self.POST_CREATE_URL_NAME), data=form_data, follow=True)
        self.assertRedirects(response, self.HOMEPAGE_URL)
        created_post = Post.objects.first()
        attribute_expected = {
            created_post.text: self.SAMPLE_TEXT,
            created_post.author: self.user,
        }
        for attribute, expected in attribute_expected.items():
            with self.subTest(attribute=attribute):
                self.assertEqual(attribute, expected)

    def test_post_edit(self):
        """Проверка редактирования поста"""
        edit_data = {
            'text': self.EDIT_TEXT
        }
        response = self.authorized_client.post(
            self.post_edit_url,
            data=edit_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        changed_post = Post.objects.get(pk=self.post_edit.pk)
        self.assertEqual(changed_post.text, edit_data['text'])

    def test_comment(self):
        """Проверка формы комментария."""
        form_data = {
            'text': self.SAMPLE_TEXT,
        }
        response = self.authorized_client.post(
            reverse(
                'add_comment',
                args=[self.user.username, self.post_edit.pk]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'post',
            args=[self.user.username, self.post_edit.pk]))
        created_comment = Comment.objects.first()
        attribute_expected = {
            created_comment.post: self.post_edit,
            created_comment.author: self.user,
            created_comment.text: self.SAMPLE_TEXT,
        }
        for attribute, expected in attribute_expected.items():
            with self.subTest(attribute=attribute):
                self.assertEqual(attribute, expected)
