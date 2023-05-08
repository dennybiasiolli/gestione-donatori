from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from avis.models import Donatore, Sesso, Sezione, StatoDonatore

User = get_user_model()


class AvisAPITestCase(APITestCase):
    fixtures = ["avis"]

    def setUp(self) -> None:
        self.user1 = User.objects.create_user("username1", "password1")
        self.user2 = User.objects.create_user("username2", "password2")
        self.sezione1 = Sezione.objects.create(utente=self.user1)
        self.sezione2 = Sezione.objects.create(utente=self.user2)
        self.sesso_f = Sesso.objects.get(codice="F")
        self.stato_donatore_attivo = StatoDonatore.objects.get(
            sezione=None, codice="Attivo"
        )
        return super().setUp()


class DonatoreApiTestCase(AvisAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.donatore1 = Donatore.objects.create(
            sesso=self.sesso_f,
            sezione=self.sezione1,
            stato_donatore=self.stato_donatore_attivo,
        )
        self.donatore2 = Donatore.objects.create(
            sesso=self.sesso_f,
            sezione=self.sezione2,
            stato_donatore=self.stato_donatore_attivo,
        )

    def test_api_calls_require_authentication(self):
        urls = (
            reverse("api-avis:donatore-list"),
            reverse("api-avis:donatore-detail", kwargs={"pk": self.donatore1.pk}),
        )
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.user1)
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filtering_by_sezione(self):
        self.client.force_login(self.user1)

        url = reverse("api-avis:donatore-list")
        response = self.client.get(url)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(len(response.json()["results"]), 1)

        url = reverse("api-avis:donatore-detail", kwargs={"pk": self.donatore2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
