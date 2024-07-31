from django.db import models
from django.utils import timezone

from user.models import CustomUser


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)

    auto_reply_timeout = models.IntegerField(default=-1)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    content = models.TextField(max_length=300)
    date_posted = models.DateTimeField(default=timezone.now)
    is_blocked = models.BooleanField(default=False)


class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    content = models.TextField(max_length=300)
    date_posted = models.DateTimeField(default=timezone.now)
