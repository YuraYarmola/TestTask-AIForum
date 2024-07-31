from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import CustomUser
from forum.models import Post, Comment, CommentReply


class PostViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )

    def test_get_posts(self):
        response = self.client.get(reverse('post-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        data = {'title': 'New Post', 'content': 'This is a new post.'}
        response = self.client.post(reverse('post-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')

    def test_update_post(self):
        data = {'title': 'Updated Post'}
        response = self.client.patch(reverse('post-get-update-delete', args=[self.post.pk]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Post')

    def test_delete_post(self):
        response = self.client.delete(reverse('post-get-update-delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment.'
        )

    def test_get_comments(self):
        response = self.client.get(reverse('post-comments-list', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'This is a test comment.')

    def test_create_comment(self):
        data = {'content': 'This is a new comment.'}
        response = self.client.post(reverse('post-comments-list', args=[self.post.pk]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a new comment.')


class CommentReplyViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment.'
        )

        self.comment_reply = CommentReply.objects.create(
            comment=self.comment,
            author=self.user,
            content='This is a test comment reply.'
        )

    def test_get_comment_replies(self):
        response = self.client.get(reverse('comment-reply-list', args=[self.comment.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'This is a test comment reply.')

    def test_create_comment_reply(self):
        data = {'content': 'This is a new comment reply.'}
        response = self.client.post(reverse('comment-reply-list', args=[self.comment.pk]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a new comment reply.')


class CommentsDailyBreakdownViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        # Create some test posts and comments
        self.post1 = Post.objects.create(
            title='Test Post 1',
            content='Content for post 1.',
            author=self.user
        )
        self.post2 = Post.objects.create(
            title='Test Post 2',
            content='Content for post 2.',
            author=self.user
        )

        # Create comments with different dates
        Comment.objects.create(
            post=self.post1,
            author=self.user,
            content='Comment 1',
            date_posted=timezone.now() - timezone.timedelta(days=1),
            is_blocked=False
        )
        Comment.objects.create(
            post=self.post1,
            author=self.user,
            content='Comment 2',
            date_posted=timezone.now() - timezone.timedelta(days=1),
            is_blocked=True
        )
        Comment.objects.create(
            post=self.post2,
            author=self.user,
            content='Comment 3',
            date_posted=timezone.now() - timezone.timedelta(days=2),
            is_blocked=False
        )

    def test_comments_daily_breakdown(self):
        date_from = (timezone.now() - timezone.timedelta(days=2)).date()
        date_to = timezone.now().date()

        url = reverse('comments-daily-breakdown')
        response = self.client.get(f'{url}?date_from={date_from}&date_to={date_to}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        expected_data = [
            {
                'date': (timezone.now() - timezone.timedelta(days=2)).date().isoformat(),
                'total_comments': 1,
                'blocked_comments': 0
            },
            {
                'date': (timezone.now() - timezone.timedelta(days=1)).date().isoformat(),
                'total_comments': 2,
                'blocked_comments': 1
            }
        ]

        self.assertEqual(data, expected_data)

    def test_missing_date_from(self):
        date_to = (timezone.now() - timezone.timedelta(days=1)).date()
        url = reverse('comments-daily-breakdown')
        response = self.client.get(f'{url}?date_to={date_to}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Both date_from and date_to parameters are required."})

    def test_missing_date_to(self):
        date_from = (timezone.now() - timezone.timedelta(days=1)).date()
        url = reverse('comments-daily-breakdown')
        response = self.client.get(f'{url}?date_from={date_from}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Both date_from and date_to parameters are required."})

    def test_invalid_date_format(self):
        date_from = 'invalid-date'
        date_to = (timezone.now() - timezone.timedelta(days=1)).date()
        url = reverse('comments-daily-breakdown')
        response = self.client.get(f'{url}?date_from={date_from}&date_to={date_to}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid date format. Use YYYY-MM-DD."})