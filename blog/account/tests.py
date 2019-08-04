from rest_framework.test import APITestCase
from django.urls import reverse


# doğru veriler ile kayıt işlemi yap.
# parola invalid olabilir.
# kullanıcı adı kullanılmış olabiir
# üye girişi yaptıysak o sayfa gözükmemeli
# token ile giriş işlemi yapıldığğında 403 hatası


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
