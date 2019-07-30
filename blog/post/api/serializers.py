from rest_framework import serializers

from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'title', 'content', 'image', 'slug', 'created', 'modified_by']


class PostUpdateCreateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = "editlendi"
        instance.image = validated_data.get('image', instance.title)
        instance.save()
        return instance

    def validate_title(self, value):
        if value == "selamet":
            raise serializers.ValidationError("Bu değer olmaz")
        return value

    def validate(self, attrs):
        print(attrs['title'])
        if attrs['title'] == 'selamet':
            raise serializers.ValidationError("Bu değer olmaz")
        return attrs
