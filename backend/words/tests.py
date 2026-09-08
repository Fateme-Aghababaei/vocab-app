import json
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from accounts.models import StudyProfile
from .models import Word, ReviewLog

from .gemini_service import GeminiError, generate_word_info, _build_prompt


@override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="test-model", GEMINI_READ_TIMEOUT=30)
class GeminiServiceTests(SimpleTestCase):
    def response(self, status=200, data=None):
        return Mock(status_code=status, ok=status < 400, json=Mock(return_value=data))

    def success(self, content=None):
        content = content if content is not None else {"definition": "A greeting", "examples": ["Hello, Sam!"]}
        return self.response(data={"candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"thought": True, "text": "private reasoning"}, {"text": json.dumps(content)}
        ]}}]})

    @patch("words.gemini_service.requests.post")
    def test_success_skips_thoughts(self, post):
        post.return_value = self.success()
        self.assertEqual(generate_word_info("hello")["definition"], "A greeting")
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 30))

    @patch("words.gemini_service.time.sleep")
    @patch("words.gemini_service.requests.post")
    def test_temporary_failure_retries_once(self, post, sleep):
        post.side_effect = [self.response(503), self.success()]
        self.assertEqual(generate_word_info("hello")["word"], "hello")
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("words.gemini_service.time.sleep")
    @patch("words.gemini_service.requests.post")
    def test_persistent_server_failure_stops(self, post, sleep):
        post.return_value = self.response(503)
        with self.assertRaises(GeminiError) as error:
            generate_word_info("hello")
        self.assertEqual(error.exception.status_code, 503)
        self.assertEqual(post.call_count, 2)

    @patch("words.gemini_service.requests.post")
    def test_client_errors_are_not_retried(self, post):
        for status, message in [(429, "quota"), (403, "denied"), (404, "model"), (400, "rejected")]:
            with self.subTest(status=status):
                post.reset_mock()
                post.return_value = self.response(status)
                with self.assertRaisesRegex(GeminiError, message):
                    generate_word_info("hello")
                post.assert_called_once()

    @patch("words.gemini_service.requests.post")
    def test_timeout_is_sanitized_and_not_retried(self, post):
        post.side_effect = requests.Timeout("secret-request-details")
        with self.assertRaises(GeminiError) as error:
            generate_word_info("hello")
        self.assertEqual(error.exception.status_code, 504)
        self.assertNotIn("secret", str(error.exception))
        post.assert_called_once()

    @patch("words.gemini_service.requests.post")
    def test_invalid_content_is_controlled_error(self, post):
        for value in [[], {"definition": ""}, {"definition": "A greeting", "examples": "bad"}]:
            with self.subTest(value=value):
                post.return_value = self.success(value)
                with self.assertRaises(GeminiError):
                    generate_word_info("hello")

    @patch("words.gemini_service.requests.post")
    def test_non_json_response_is_controlled_error(self, post):
        post.return_value = self.response()
        post.return_value.json.side_effect = ValueError("not JSON")
        with self.assertRaises(GeminiError):
            generate_word_info("hello")

    @override_settings(GEMINI_MODEL="gemini-3.6-flash")
    @patch("words.gemini_service.requests.post")
    def test_vocabulary_uses_minimal_thinking(self, post):
        post.return_value = self.success()
        generate_word_info("hello")
        self.assertEqual(post.call_args.kwargs["json"]["generationConfig"]["thinkingConfig"],
                         {"thinkingLevel": "minimal"})

    @patch("words.gemini_service.requests.post")
    def test_pronunciation_is_preserved(self, post):
        post.return_value = self.success({"definition": "A greeting", "pronunciation": "/həˈloʊ/"})
        self.assertEqual(generate_word_info("hello")["pronunciation"], "/həˈloʊ/")

    @patch("words.gemini_service.requests.post")
    def test_missing_pronunciation_is_optional(self, post):
        post.return_value = self.success()
        self.assertEqual(generate_word_info("hello")["pronunciation"], "")

    @patch("words.gemini_service.requests.post")
    def test_invalid_pronunciation_is_rejected(self, post):
        for value in [None, [], 123, "a" * 201]:
            with self.subTest(value=value):
                post.return_value = self.success({"definition": "A greeting", "pronunciation": value})
                with self.assertRaisesRegex(GeminiError, "pronunciation"):
                    generate_word_info("hello")


class LanguageIsolationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='learner')
        StudyProfile.objects.create(user=self.user, languages=['en', 'es'], active_language='en')
        self.client.force_authenticate(self.user)
        self.english = Word.objects.create(user=self.user, word='hello', categories=['English only'])
        self.spanish = Word.objects.create(user=self.user, language='es', word='hola', categories=['Spanish only'])
        other = User.objects.create_user(username='other')
        Word.objects.create(user=other, language='es', word='privado')

    def test_library_due_categories_and_stats_are_scoped(self):
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='es')
        response = self.client.get('/api/words/')
        self.assertEqual([word['word'] for word in response.data['results']], ['hola'])
        self.assertEqual([word['word'] for word in self.client.get('/api/words/due/').data], ['hola'])
        categories = self.client.get('/api/words/categories/').data
        self.assertIn('Spanish only', categories)
        self.assertNotIn('English only', categories)
        self.client.post(f'/api/words/{self.spanish.pk}/review/', {'quality': 2})
        self.assertEqual(self.client.get('/api/stats/').data['reviewed_today'], 1)
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='en')
        stats = self.client.get('/api/stats/').data
        self.assertEqual(stats['total_words'], 1)
        self.assertEqual(stats['reviewed_today'], 0)
        self.english.refresh_from_db()
        self.assertEqual(self.english.repetitions, 0)

    def test_cross_language_detail_edit_delete_and_review_are_rejected(self):
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='es')
        url = f'/api/words/{self.english.pk}/'
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.patch(url, {'word': 'changed'}).status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertEqual(self.client.post(url + 'review/', {'quality': 2}).status_code, 404)
        self.assertFalse(ReviewLog.objects.exists())

    def test_same_spelling_allowed_in_different_languages_and_ipa_roundtrip(self):
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='es')
        response = self.client.post('/api/words/', {'word': 'hello', 'pronunciation': '/test/', 'language': 'en'})
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['language'], 'es')
        self.assertEqual(response.data['pronunciation'], '/test/')
        self.assertEqual(self.client.post('/api/words/', {'word': 'hello'}).status_code, 400)
        url = f"/api/words/{response.data['id']}/"
        self.assertEqual(self.client.patch(url, {'word': 'hola'}).status_code, 400)
        self.assertEqual(self.client.patch(url, {'pronunciation': '/edited/'}).status_code, 200)
        self.assertEqual(self.client.get(url).data['pronunciation'], '/edited/')

    def test_unselected_language_rejected_and_active_language_used_by_default(self):
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='ja')
        self.assertEqual(self.client.get('/api/words/').status_code, 400)
        self.client.credentials()
        self.client.patch('/api/auth/me/', {'language': 'es'})
        self.assertEqual(self.client.get('/api/words/').data['results'][0]['word'], 'hola')

    @patch('words.views.generate_word_info')
    def test_generation_receives_request_language(self, generate):
        generate.return_value = {'word': 'hola', 'definition': 'A greeting'}
        self.client.credentials(HTTP_X_STUDY_LANGUAGE='es')
        self.assertEqual(self.client.post('/api/words/generate/', {'word': 'hola'}).status_code, 200)
        generate.assert_called_once_with('hola', 'es')

    def test_prompt_uses_target_language(self):
        prompt = _build_prompt('سلام', 'fa')
        self.assertIn('standard Persian IPA', prompt)
        self.assertIn('collocations in Persian', prompt)
        self.assertNotIn('US English', prompt)
        self.assertIn('US English IPA', _build_prompt('hello'))
