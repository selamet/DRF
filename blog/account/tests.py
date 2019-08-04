from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse


# doğru veriler ile kayıt işlemi yap.
# parola invalid olabilir.
# kullanıcı adı kullanılmış olabiir
# üye girişi yaptıysak o sayfa gözükmemeli
# token ile giriş işlemi yapıldığğında 403 hatası
from rest_framework.utils import json


class UserRegistrationTestCase(APITestCase):
    url = reverse("account:register")
    url_login = reverse("token_obtain_pair")

    def test_user_registration(self):
        """
            doğru veriler ile kayıt işlemi.

        """
        data = {"username": "selamettest",
                "password": "deneme123"
                }

        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_user_invalid_password(self):
        """
            invalid password ile kayıt işlemi.

        """
        data = {"username": "selamettest",
                "password": "2"
                }

        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_unique_name(self):
        """
            benzersiz isim testi

        """
        self.test_user_registration()
        data = {"username": "selamettest",
                "password": "dogru sifre"
                }

        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_user_authenticated_registration(self):
        """
           session ile giriş yapmış kullanıcı sayfayı görememeli.

        """

        self.test_user_registration()
        self.client.login(username="selamettest", password='deneme123')
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_user_authenticated_token_registration(self):
        """
           token ile giriş yapmış kullanıcı sayfayı görememeli.

        """

        self.test_user_registration()

        data = {"username": "selamettest",
                "password": "deneme123"
                }

        response = self.client.post(self.url_login, data=data)
        self.assertEqual(200, response.status_code)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response_2 = self.client.get(self.url)
        self.assertEqual(403, response_2.status_code)


class UserLogin(APITestCase):
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        # testler çalışmadan önce çalışır
        self.username = "selamet"
        self.password = "parola123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_token(self):
        response = self.client.post(self.url_login, {"username": "selamet", "password": "parola123"})
        self.assertEqual(200, response.status_code)
        print(json.loads(response.content))
        self.assertTrue("access" in json.loads(response.content))


    def test_user_invalid_data(self):
        response = self.client.post(self.url_login, {"username": "sel12amet", "password": "parola123"})
        self.assertEqual(401, response.status_code)

    def test_user_empty_data(self):
        response = self.client.post(self.url_login, {"username": "", "password": ""})
        self.assertEqual(400, response.status_code)

