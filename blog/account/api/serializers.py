from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from account.models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'note', 'twitter')


class UserSerializer(ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'profile')

    def update(self, instance, validated_data):
        profile = validated_data.pop('profile')
        profile_serializer = ProfileSerializer(instance=instance.profile, data=profile)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        return super(UserSerializer, self).update(instance, validated_data)


class ChangePasswordSerializer(Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
