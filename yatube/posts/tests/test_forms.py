import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug1',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в post_create."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма изменяет запись в post_edit."""
        post = Post.objects.create(
            text='Тестовый текст для редактирования',
            author=self.user)
        post_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = CommentForm()

    def setUp(self):
        self.notauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_add_comment_authorized(self):
        '''Проверка создания комментария авторизованным клиентом.'''
        comment_count = Comment.objects.count()
        post = Post.objects.create(
            text='Тестовый текст для редактирования',
            author=self.user)
        form_data = {
            'text': 'Комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_post_detail_add_comment_notauthorized(self):
        '''Проверка создания комментария неавторизованным клиентом.'''
        comment_count = Comment.objects.count()
        post = Post.objects.create(
            text='Тестовый текст для редактирования',
            author=self.user)
        form_data = {
            'text': 'Комментарий',
        }
        self.notauthorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
