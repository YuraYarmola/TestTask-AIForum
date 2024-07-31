from django.urls import path
from .views import *

urlpatterns = [
    path('post/', PostListView.as_view(), name='post-list-create'),
    path('post/<int:pk>/', PostGetUpdateDeleteView.as_view(), name='post-get-update-delete'),
    path("post/<int:post_id>/comment/", CommentListCreateView.as_view(), name="post-comments-list"),
    path("comment/<int:comment_id>/reply/", CommentReplyListCreateView.as_view(), name="comment-reply-list"),
    path('comments-daily-breakdown/', CommentsDailyBreakdownView.as_view(), name='comments-daily-breakdown'),
]


