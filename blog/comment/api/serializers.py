from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from comment.models import Comment
from post.models import Post


class CommentCreateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['created', ]  # bütün fieldleri kabul ediyoruz created hariç

    def validate(self, attrs):
        if (attrs["parent"]):
            if attrs['parent'].post != attrs['post']:
                raise serializers.ValidationError('Someting went wrong')
        return attrs


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'id', 'email')


class PostCommentSerialize(ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'slug', 'id')


class CommentListSerializer(ModelSerializer):
    replies = SerializerMethodField()
    user = UserSerializer()
    post = PostCommentSerialize()

    class Meta:
        model = Comment
        fields = '__all__'
        # depth = 1 # Tüm verileri getirir

    def get_replies(self, obj):
        if obj.any_children:
            return CommentListSerializer(obj.children(), many=True).data


class CommentDeleteUpdateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
