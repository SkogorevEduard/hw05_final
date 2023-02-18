from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_urls_exists_at_desired_location(self):
        """Проверка status_code для авторизованного пользователя."""
        url_names = {
            reverse('posts:index'): 200,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 200,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 200,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): 200,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): 200,
            reverse('posts:post_create'): 200,
            '/unexisting_page/': 404,
        }
        for url, status in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_guest_urls_exists_at_desired_location(self):
        """Проверка status_code для неавторизованного пользователя."""
        url_names = {
            reverse('posts:index'): 200,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 200,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 200,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): 200,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): 302,
            reverse('posts:post_create'): 302,
            '/unexisting_page/': 404,
        }
        for url, status in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
