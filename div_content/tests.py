from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Movie


class TestMovieAPI(APITestCase):
    @classmethod
    def setUp(cls):
        # Vytvoření testovacího filmu v databázi
        Movie.objects.create(
            movieid=1,
            title='Testovací film',
            titlecz='Testovací film CZ',
            special=1,
            url='https://www.example.com',
            img='/static/img/test.jpg',
            description='Popis testovacího filmu',
            releaseyear='2022',
            duration=120,
            language='EN',
            budget=1000000,
            adult='N',
            popularity='7.8',
            idcsfd='12345',
            idimdb='67890',
            iddiv='54321',
            averagerating=8.5
        )
        # Vytvoření admin uživatele
        cls.admin = User.objects.create_user(username="admin", email='admin@admin.com', password='password', is_staff=1)

        # Vytvoření obyčejného testovacího uživatele
        cls.user = User.objects.create_user(username="test", email='abcd@abcd.cz', password='abcdabcd')

    def test_get_movie_list(self):
        # Test přístupu k seznamu filmů bez a s "secret key"
        url = reverse('movie-list')
        # Očekáváme zakázání přístupu bez "secret key"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Přístup s "secret key" by měl být povolen
        response = self.client.get(url, **{'HTTP_X_SECRET_KEY': 'váš_velmi_tajný_klíč'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_movie_detail(self):
        # Test získání detailů konkrétního filmu
        url = reverse('movie-detail-get', args=[1])
        # Bez "secret key" by měl být přístup zakázán
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # S "secret key" by měl být přístup povolen
        response = self.client.get(url, **{'HTTP_X_SECRET_KEY': 'váš_velmi_tajný_klíč'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_movie_create(self):
        # Test vytvoření nového filmu
        url = reverse('movie-new')
        data = {
            'movieid': 2,
            'adult': 1,
            'title': 'Nový film',
            'url': 'novy_film',
        }
        # Bez autentizace by měl být přístup zakázán
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako běžný uživatel, přístup by měl být stále zakázán
        self.client.login(username='test', password='abcdabcd')
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako admin, nyní by mělo být vytvoření filmu povoleno
        self.client.login(username='admin', password='password')
        response3 = self.client.post(url, data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)

        # Test chybného požadavku (např. duplicitní movieid)
        error = {
            'movieid': 1,
            'adult': 1,
            'title': 'Nový film',
            'url': 'novy_film',
        }
        response4 = self.client.post(url, error, format='json')
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_movie_update(self):
        # Test aktualizace filmu
        url = reverse('movie-detail-patch', args=[1])
        updated_data = {
            'movieid': 1,
            'title': 'Aktualizovaný název filmu',
        }
        # Bez přihlášení, aktualizace by neměla být povolena
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako běžný uživatel, aktualizace by stále neměla být povolena
        self.client.login(username='test', password='abcdabcd')
        response2 = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako admin, aktualizace by měla být nyní povolena
        self.client.login(username='admin', password='password')
        response3 = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        # Ověření, že aktualizace proběhla správně
        updated_movie = Movie.objects.get(pk=updated_data['movieid'])
        self.assertEqual(updated_movie.title, updated_data['title'])

    def test_delete_movie_delete(self):
        # Test smazání filmu
        url = reverse('movie-delete', args=[1])
        # Bez přihlášení by měl být přístup zakázán
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako běžný uživatel, smazání by stále nemělo být povoleno
        self.client.login(username='test', password='abcdabcd')
        response2 = self.client.delete(url)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        # Přihlášení jako admin, smazání by mělo být nyní povoleno
        self.client.login(username='admin', password='password')
        response3 = self.client.delete(url)
        self.assertEqual(response3.status_code, status.HTTP_204_NO_CONTENT)
        # Test opětovného smazání již smazaného filmu by měl vrátit 404
        response4 = self.client.delete(url)
        self.assertEqual(response4.status_code, status.HTTP_404_NOT_FOUND)