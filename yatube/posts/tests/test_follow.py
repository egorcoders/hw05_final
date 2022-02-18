from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse
from posts.models import Follow, Post

User = get_user_model()


class PostFollowTest(TestCase):
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
            text='Post text',
            author=cls.author
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.author
        )

    def test_post_profile_follow(self):
        """Проверка, возможно ли подписаться на автора поста."""
        self.authorized_client1.get(
            reverse('posts:profile_follow', kwargs={'username': 'author'})
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.user1,
            ).exists(),
        )

    def test_post_profile_unfollow(self):
        """Проверка, возможно ли отписаться от автора поста."""
        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'author'})
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.user2
            ).exists()
        )

    def test_post_follow_index_follower(self):
        """Проверка, находится ли новый пост в ленте подписчика."""
        response_follower = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        post_follow = response_follower.context.get('page_obj')[0]
        self.assertEqual(post_follow, self.post)

    def test_post_follow_index_unfollower(self):
        """Проверка находится ли пост в ленте не подписчика."""
        response_unfollower = self.authorized_client1.get(
            reverse('posts:follow_index')
        )
        post_unfollow = response_unfollower.context.get('page_obj')
        self.assertEqual(post_unfollow.object_list.count(), 0)
