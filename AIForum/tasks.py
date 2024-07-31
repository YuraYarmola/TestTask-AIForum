from celery import shared_task
from forum.models import Comment, CommentReply, Post
from utils.AIHelper import comment_reply


@shared_task
def reply_to_comment(post_id, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        post = Post.objects.get(pk=post_id)
        content = comment_reply(str(post.content), str(comment.content))
        if not comment.is_blocked:
            CommentReply.objects.create(
                comment=comment,
                author=post.author,
                content=content,
            )
    except Comment.DoesNotExist:
        print(f"Comment with id {comment_id} does not exist.")
    except Post.DoesNotExist:
        print(f"Post with id {post_id} does not exist.")
