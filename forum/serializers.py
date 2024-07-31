from pydantic import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from utils.AIHelper import is_text_toxic
from forum.models import Post, Comment, CommentReply


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author', "date_posted", 'is_blocked', "pk")

    def create(self, validated_data):
        if is_text_toxic(validated_data['content']) or is_text_toxic(validated_data['title']):
            validated_data['is_blocked'] = True
        else:
            validated_data['is_blocked'] = False
        validated_data['author'] = self.context['request'].user
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('content'):
            if is_text_toxic(validated_data['content']):
                validated_data['is_blocked'] = True
            else:
                validated_data['is_blocked'] = False

        if validated_data.get('title') and not validated_data.get('is_blocked', False):
            if is_text_toxic(validated_data['title']):
                validated_data['is_blocked'] = True
            else:
                validated_data['is_blocked'] = False

        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance


class CommentReplySerializer(ModelSerializer):

    class Meta:
        model = CommentReply
        fields = '__all__'
        read_only_fields = ('author', "date_posted", 'is_blocked', "pk", "comment")

    def create(self, validated_data):
        if is_text_toxic(validated_data['content']):
            validated_data['is_blocked'] = True
        else:
            validated_data['is_blocked'] = False

        validated_data['author'] = self.context['request'].user
        return CommentReply.objects.create(**validated_data)

    def update(self, instance, validated_data):
        comment = self.context["comment_id"]
        validated_data['comment'] = Comment.objects.get(pk=comment)
        if validated_data.get('content'):
            if is_text_toxic(validated_data['content']):
                validated_data['is_blocked'] = True
            else:
                validated_data['is_blocked'] = False
        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance


class CommentSerializer(ModelSerializer):
    reply = serializers.SerializerMethodField("get_reply")

    class Meta:
        model = Comment
        fields = ("content", 'author', "date_posted", 'is_blocked', "post", "pk", "reply",)
        read_only_fields = ("date_posted", 'is_blocked', "pk", "author", "post")

    def get_reply(self, obj):
        comment = Comment.objects.get(pk=obj.pk)
        comment_reply_serializer = CommentReplySerializer(data=CommentReply.objects.filter(comment=comment), many=True)
        comment_reply_serializer.is_valid()
        return comment_reply_serializer.data

    def create(self, validated_data):
        if is_text_toxic(validated_data['content']):
            validated_data['is_blocked'] = True
        else:
            validated_data['is_blocked'] = False
        validated_data['author'] = self.context['author']
        validated_data['post'] = self.context["post"]
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('content'):
            if is_text_toxic(validated_data['content']):
                validated_data['is_blocked'] = True
            else:
                validated_data['is_blocked'] = False
        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance



