from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    '''Форма для создания нового поста.'''

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }

    def clean_data(self):
        data = self.cleaned_data['text']
        if '' in data.lower():
            raise forms.ValidationError('Поле обязательно для заполнения')
        return data


class CommentForm(forms.ModelForm):
    '''Форма для создания нового комментария.'''

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Добавить комментарий:'}
