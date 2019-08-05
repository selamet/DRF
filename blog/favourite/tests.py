import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from favourite.models import Favourite
from post.models import Post


class FavouriteCreateList(APITestCase):
    url = reverse("favourite:list")
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "selamet"
        self.password = "test1234"
        self.post = Post.objects.create(title="baslık", content="içerik")
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.test_jwt_authentication()

    def test_jwt_authentication(self):
        response = self.client.post(self.url_login, data={"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_add_favourite(self):
        data = {
            "content": "favla",
            "user": self.user.id,
            "post": self.post.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_user_fav(self):
        self.test_add_favourite()
        response = self.client.get(self.url)
        self.assertTrue(len(json.loads(response.content)["results"])
                        == Favourite.objects.filter(user=self.user).count())


class FavouriteUpdateDelete(APITestCase):
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "selamet"
        self.password = "test1234"
        self.post = Post.objects.create(title="baslık", content="içerik")
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username="selamet2", password=self.password)
        self.favourite = Favourite.objects.create(content="deneme", post=self.post, user=self.user)
        self.url = reverse("favourite:update-delete", kwargs={"pk": self.favourite.pk})
        self.test_jwt_authentication()

    def test_jwt_authentication(self, username="sealmet", password="test1234"):
        response = self.client.post(self.url_login, data={"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_fav_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

    # başkası bizim postumuzu silemez
    def test_fav_delete_different_user(self):
        self.test_jwt_authentication("selamet2")
        response = self.client.delete(self.url)
        self.assertTrue(403, response.status_code)

    def test_fav_update(self):
        data = {
            "content": "içeriğimiz",
            "post": self.post.id,
            "user": self.user.id
        }

        response = self.client.put(self.url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(Favourite.objects.get(id=self.favourite.id).content == data["content"])

    # başkası bizim yerimize update yaparsa
    def test_fav_update_different_user(self):
        self.test_jwt_authentication("selamet2")
        data = {
            "content": "içerik 123",
            "user": self.user2.id
        }

        response = self.client.put(self.url, data)
        self.assertTrue(403, response.status_code)

    def test_unauthentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)
