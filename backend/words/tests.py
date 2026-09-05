import json
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings

from .gemini_service import GeminiError, generate_word_info


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
