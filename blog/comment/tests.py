from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from comment.models import Comment
from post.models import Post
import json


class CommentCreate(APITestCase):
    login_url = reverse("token_obtain_pair")

    def setUp(self):
        self.url = reverse("comment:create")
        self.url_list = reverse("comment:list")
        self.username = "selamet"
        self.password = "parola123"
        self.post = Post.objects.create(title="deneme", content="içerik")
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.parent_comment = Comment.objects.create(content="içerik yorum", user=self.user, post=self.post)
        self.test_jwt_authentication()

    def test_jwt_authentication(self):
        response = self.client.post(self.login_url, data={"username": "selamet", "password": "parola123"})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_comment(self):
        data = {
            "content": "Yapalım bakalım yorummm",
            "user": self.user.id,
            "post": self.post.id,
            "parent": ""
        }
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_create_child_comment(self):
        data = {
            "content": "Yapalım bakalım yorumm",
            "user": self.user.id,
            "post": self.post.id,
            "parent": self.parent_comment.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_comment_list(self):
        self.test_create_comment()
        response = self.client.get(self.url_list, {'q': self.post.id})
        self.assertTrue(response.data["count"] == Comment.objects.filter(post=self.post).count())


class CommentUpdateDeleteTest(APITestCase):
    login_url = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "selamet1234"
        self.password = "parola1234"
        self.post = Post.objects.create(title="deneme", content="içerik")
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username="selamet5332", password=self.password)
        self.comment = Comment.objects.create(content="içerik yorum", user=self.user, post=self.post)
        self.url = reverse("comment:update", kwargs={'pk': self.comment.pk})
        self.test_jwt_authentication()

    def test_jwt_authentication(self, username="selamet1234", password="parola1234"):
        response = self.client.post(self.login_url, data={"username": username, "password": password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_delete_comment(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_other_user(self):
        self.test_jwt_authentication("selamet5332")
        response = self.client.delete(self.url)
        self.assertEqual(403, response.status_code)
        self.assertTrue(Comment.objects.get(pk=self.comment.pk))

    def test_update_comment(self):
        response = self.client.put(self.url, data={"content": "icerik"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(Comment.objects.get(pk=self.comment.id).content, "icerik")

    def test_update_comment_other_user(self):
        self.test_jwt_authentication("selamet5332")
        response = self.client.put(self.url, data={"content": "icerik"})
        self.assertEqual(403, response.status_code)
        self.assertNotEqual(Comment.objects.get(pk=self.comment.id).content, "icerik")

    def test_unauthorization(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)
