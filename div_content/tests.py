from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Movie,User

class APITest(APITestCase):

    @classmethod
    def setUp(cls):
        # Nastavení testovacích dat
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
        # user = User.objects.create_user(username="test", email='abcd@abcd.cz', password='abcdabcd')
        # user.save()

    def test_get_movie_list(self):
        url = reverse('movie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_movie_detail(self):
        url = reverse('movie-detail-get', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_post_movie_create(self):
    #     url = reverse('movie-new')
    #     data = {
    #     'movieid': 2,
	#  	'adult': 1,
    #     'title': 'Nový film',
	# 	'url':'novy_film',
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.client.login(username='test', email='abcd@abcd.cz', password='abcdabcd')
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_patch_movie_update(self):
    #     url = reverse('movie-detail-patch', args=[1])
    #     updated_data = {
	# 	'movieid':1,
    #     'title': 'detail_wtf',
    #     }
    #     response = self.client.patch(url, updated_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.client.login(username='test', email='abcd@abcd.cz', password='abcdabcd')
    #     response = self.client.patch(url, updated_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     updated_movie = Movie.objects.get(pk=updated_data['movieid'])
    #     self.assertEqual(updated_movie.title, updated_data['title'])
    #
    # def test_delete_movie_delete(self):
    #     url = reverse('movie-delete', args=[1])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.client.login(username='test', email='abcd@abcd.cz', password='abcdabcd')
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

