from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse
from posts.models import Comment, Post

User = get_user_model()


class PostCommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.author = User.objects.create(username='author')
        cls.guest_client = Client()
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author
        )

    def test_post_comment_guest_user(self):
        """
        Проверка неавторизированного пользователя
        на редирект при попытке комментирования
        и невозможность комментирования.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response_guest = self.guest_client.post(
            reverse('posts:post_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        redirect_page = reverse('login') + '?next=%2Fposts%2F1%2Fcomment%2F'
        self.assertRedirects(
            response_guest,
            redirect_page,
            msg_prefix='Ошибка редиректа неавторизованного пользователя.',
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count,
            'Ошибка изменённого количества комментариев.',
        )

    def test_post_comment_authorized_user(self):
        """
        Проверка авторизированного пользователя
        на редирект после комментирования,
        возможность комментирования,
        изменяемое количество комментариев и их добавление.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response_authorized = self.authorized_client1.post(
            reverse('posts:post_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response_authorized,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            msg_prefix='Ошибка редиректа.',
        )
        self.assertEqual(
            response_authorized.context.get('comments')[0].text,
            'Test comment',
            'Ошибка нахождения комментария на странице поста.',
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'Ошибка изменения количества комментариев.'
        )
        self.assertTrue(
            Comment.objects.filter(text='Test comment').exists(),
            'Ошибка нахождения добавленного комментария.'
        )
