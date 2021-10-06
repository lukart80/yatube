from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста',
                  'group': 'Выберите группу',
                  'image': 'Выберите изображение'}
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу вашего поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Ваш комментарий'}
        help_texts = {'text': 'Не более 500 знаков'}
