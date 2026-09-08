from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import StudyProfile


class StudyPreferencesTests(APITestCase):
    def test_signup_with_selected_language(self):
        response = self.client.post('/api/auth/register/', {
            'email': 'learner@example.com', 'password': 'testing-a-strong-password-21',
            'language': 'fa',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['languages'], ['fa'])
        self.assertEqual(response.data['user']['active_language'], 'fa')

    def test_existing_user_defaults_and_preferences_persist(self):
        user = User.objects.create_user(username='learner', password='password')
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get('/api/auth/me/').data['languages'], ['en'])
        response = self.client.patch('/api/auth/me/', {'language': 'es'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['languages'], ['en', 'es'])
        self.client.patch('/api/auth/me/', {'language': 'es'})
        profile = StudyProfile.objects.get(user=user)
        self.assertEqual(profile.languages, ['en', 'es'])
        self.assertEqual(self.client.get('/api/auth/me/').data['active_language'], 'es')
        self.client.patch('/api/auth/me/', {'language': 'en'})
        self.assertEqual(self.client.get('/api/auth/me/').data['languages'], ['en', 'es'])

    def test_unsupported_language_and_unauthenticated_updates_rejected(self):
        self.assertEqual(self.client.patch('/api/auth/me/', {'language': 'es'}).status_code, 401)
        user = User.objects.create_user(username='learner')
        self.client.force_authenticate(user)
        self.assertEqual(self.client.patch('/api/auth/me/', {'language': 'invalid'}).status_code, 400)

    def test_preferences_belong_to_current_user(self):
        first = User.objects.create_user(username='first')
        second = User.objects.create_user(username='second')
        self.client.force_authenticate(first)
        self.client.patch('/api/auth/me/', {'language': 'ja'})
        self.client.force_authenticate(second)
        self.assertEqual(self.client.get('/api/auth/me/').data['languages'], ['en'])

    def test_language_catalog_is_available_before_signup(self):
        response = self.client.get('/api/auth/languages/')
        self.assertEqual(response.status_code, 200)
        self.assertIn({'code': 'fa', 'name': 'Persian'}, response.data)
