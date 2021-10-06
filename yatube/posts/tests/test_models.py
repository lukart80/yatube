from django.db import IntegrityError
from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    USER_NAME = 'test_user'
    SAMPLE_TEXT = 'т'
    USER_NAME2 = 'test_user2'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.user2 = User.objects.create_user(username=cls.USER_NAME2)
        cls.post = Post.objects.create(
            text=cls.SAMPLE_TEXT * 50,
            author=cls.user
        )
        cls.group = Group.objects.create(
            title=cls.SAMPLE_TEXT,
            description=cls.SAMPLE_TEXT,
        )
        cls.comment = Comment.objects.create(
            text=cls.SAMPLE_TEXT * 50,
            author=cls.user,
            post=cls.post
        )

    def test_post_str_method(self):
        """Проверить, что отображение поста не превышает 15 символов."""
        post = PostModelTest.post
        post_string_rep = post.__str__()
        self.assertEqual(post_string_rep, self.SAMPLE_TEXT * 15)

    def test_group_str_method(self):
        """Проверить, что название группы корректно отображается."""
        group = PostModelTest.group
        group_string_rep = group.__str__()
        self.assertEqual(group_string_rep, self.SAMPLE_TEXT)

    def test_comment_str_method(self):
        """Проверить, что комментарий корректно отображается."""
        comment = PostModelTest.comment
        comment_string_rep = comment.__str__()
        self.assertEqual(comment_string_rep, self.SAMPLE_TEXT * 15)

    def test_follow_unique_constrain(self):
        """Проверить, что подписки не могут повторяться."""
        Follow.objects.create(author=self.user2, user=self.user)
        self.assertRaises(IntegrityError, Follow.objects.create, **{
            'user': self.user,
            'author': self.user2,
        })
