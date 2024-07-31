from datetime import timedelta

from django.utils import timezone
from pydantic import ValidationError
from rest_framework import generics, permissions
from .models import Post, Comment, CommentReply
from .serializers import PostSerializer, CommentReplySerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from AIForum.tasks import reply_to_comment


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostGetUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(pk=kwargs['pk'])
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({'error': 'You do not have permission to edit this post'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({'error': 'You do not have permission to edit this post'}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(pk=self.kwargs['post_id'])
        author = request.user
        comment_serializer = CommentSerializer(data=request.data, context={'post': post, 'author': author})

        if comment_serializer.is_valid():
            comment = comment_serializer.save()
            post = Post.objects.get(pk=self.kwargs['post_id'])

            if post.auto_reply_timeout > 0:
                reply_delay = timedelta(seconds=post.auto_reply_timeout)
                reply_time = timezone.now() + reply_delay
                reply_to_comment.apply_async((post.id, comment.id), eta=reply_time)
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(pk=post_id)
        return Comment.objects.filter(post=post)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise ValidationError({'post': 'This post does not exist.'})

        serializer.save(author=self.request.user, post=post)


class CommentReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.get(pk=comment_id)
        return CommentReply.objects.filter(comment=comment)

    def perform_create(self, serializer):
        comment_id = self.kwargs.get('comment_id')
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Post.DoesNotExist:
            raise ValidationError({'post': 'This post does not exist.'})
        serializer.save(author=self.request.user, comment=comment)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['comment_id'] = self.kwargs.get('comment_id')  # Pass additional context
        return context


class CommentsDailyBreakdownView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if not date_from or not date_to:
            return Response(
                {"error": "Both date_from and date_to parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_from_parsed = parse_date(date_from)
            date_to_parsed = parse_date(date_to)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not date_from_parsed or not date_to_parsed:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        comments = Comment.objects.filter(date_posted__range=[date_from_parsed, date_to_parsed])
        daily_stats = comments.annotate(date=TruncDate('date_posted')).values('date').annotate(
            total_comments=Count('id'),
            blocked_comments=Count('id', filter=Q(is_blocked=True))
        ).order_by('date')

        return Response(daily_stats, status=status.HTTP_200_OK)
