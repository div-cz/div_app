from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from .models import Movie


class TestMovieAPI(APITestCase):
    @classmethod
    def setUp(cls):
        # Create test Movie
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

        # Create test Users
        cls.user = User.objects.create_user(username="test", email='abcd@abcd.cz', password='abcdabcd')
        #cls.staff = User.objects.create_user(username="staff", email='staff@abcd.cz', password='abcdabcd', is_staff=True)
        cls.superuser = User.objects.create_user(username="supertest", email='super@abcd.cz', password='abcdabcd', is_superuser=True)

    def get_csrf_token(self):
        # Method to get CSRF token
        response = self.client.get('/accounts/csrf_token/')
        csrftoken = response.cookies['csrftoken'].value  # CSRF Token is used in cookies
        return csrftoken

    def login_user(self,user):
        # Method to log in user
        response = self.client.get('/accounts/csrf_token/')
        csrftoken = response.cookies['csrftoken'].value

        self.client.credentials(
            HTTP_ACCEPT='application/json',
            HTTP_X_CSRFTOKEN=csrftoken,
            HTTP_REFERER='http://localhost:8000/accounts/csrf_token/',
        )
        login_data = {
            "login": user.email,
            "password": "abcdabcd",
        }
        # Login with CSRF token
        response = self.client.post('/accounts/login/', data=login_data)
        return response

    def logout(self):
        test = self.client.get('/accounts/logout/')
        # print(test.wsgi_request.user)
        return (test)

    def test_get_movie_list(self): ##METHOD TO GET ALL MOVIES
        url = reverse('movie-list')

        #Get movies without authorization
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #Try to login
        login_response = self.login_user(self.user)
        self.assertEqual(login_response.status_code,status.HTTP_200_OK)

        #Try to get all movies
        response_ok = self.client.get(url)
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        #Try to post url
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_movie_detail(self): ##METHOD TO GET MOVIE BY PK
        url = reverse('movie-detail-get',args=[1])
        url_non_exist = reverse('movie-detail-get', args=[2])

        # Get movies without authorization
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Try to login
        login_response = self.login_user(self.user)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Try to get movie with details
        response_ok = self.client.get(url)
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        # Try to post method
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to get non-existng movie
        response_non_exist = self.client.get(url_non_exist)
        self.assertEqual(response_non_exist.status_code, status.HTTP_404_NOT_FOUND)
    #
    def test_post_movie_create(self): ##METHOD TO CREATE MOVIE
        url = reverse('movie-new')
        data = {
            'movieid': 2,
            'adult': 1,
            'title': 'Nový film',
            'url': 'novy_film',
        }
        # Get movies without authorization
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Try to login as normal user
        login_response = self.login_user(self.user)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Try to create Movie as normaluser
        response_success = self.client.post(url, data, format='json')
        self.assertEqual(response_success.status_code, status.HTTP_403_FORBIDDEN)

        # Logout and test is any user is not authenticated
        self.logout()
        self.assertNotIn('_auth_user_id', self.client.session)

        # Try to login as superuser
        login_response = self.login_user(self.superuser)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Try to create Movie as superuser
        response_success = self.client.post(url, data, format='json')
        self.assertEqual(response_success.status_code, status.HTTP_201_CREATED)

        error = {
            'movieid': 1,
            'adult': 1,
            'title': 'Nový film',
            'url': 'novy_film',
        }

        # Trying to create movie with existing movieid
        response_exists = self.client.post(url, error, format='json')
        self.assertEqual(response_exists.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_movie_update(self): ##METHOD TO UPDATE MOVIE
        url = reverse('movie-detail-patch', args=[1])
        url_non_exist = reverse('movie-detail-patch', args=[2])
        updated_data = {
            'movieid':1,
            'title': 'čučua !',
        }
        updated_data_non_exist = {
            'movieid': 2,
            'title': 'čučua !',
        }

        #Get movies without authorization
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Try to login
        login_response = self.login_user(self.superuser)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Update data
        response_update = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)

        # Test that title is sucessfully updated
        updated_movie = Movie.objects.get(pk=updated_data['movieid'])
        self.assertEqual(updated_movie.title, updated_data['title'])

        # Test to update nonexisting movie
        response_update_nonexist = self.client.patch(url_non_exist, updated_data_non_exist, format='json')
        self.assertEqual(response_update_nonexist.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_movie_delete(self): ##METHOD TO DELETE MOVIE
        url = reverse('movie-delete', args=[1])

        # Delete movie without authorization
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Try to login
        login_response = self.login_user(self.superuser)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Delete movie
        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        # Testing delete same Movie again
        response_deleted = self.client.delete(url)
        self.assertEqual(response_deleted.status_code, status.HTTP_404_NOT_FOUND)