import json
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings

from .gemini_service import GeminiError, generate_word_info


@override_settings(
    GEMINI_API_KEYS=["test-key-1", "test-key-2"],
    GEMINI_MODELS=["test-model-1", "test-model-2"],
    GEMINI_READ_TIMEOUT=30
)
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
        result = generate_word_info("hello")
        self.assertEqual(result["definition"], "A greeting")
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 30))

    @patch("words.gemini_service.requests.post")
    def test_rotates_key_on_429(self, post):
        # تست اینکه کلید اول 429 می‌دهد و بلافاصله با کلید دوم موفق می‌شود
        post.side_effect = [self.response(429), self.success()]
        result = generate_word_info("hello")
        self.assertEqual(result["word"], "hello")
        self.assertEqual(post.call_count, 2)
        # کلید اول با کلید دوم تفاوت دارد
        first_key = post.call_args_list[0].kwargs["headers"]["x-goog-api-key"]
        second_key = post.call_args_list[1].kwargs["headers"]["x-goog-api-key"]
        self.assertNotEqual(first_key, second_key)

    @patch("words.gemini_service.requests.post")
    def test_falls_back_to_next_model_on_503(self, post):
        # وقتی مدل اول 503 می‌دهد، بلافاصله روی مدل دوم تست می‌کند
        post.side_effect = [self.response(503), self.success()]
        result = generate_word_info("hello")
        self.assertEqual(result["word"], "hello")
        self.assertEqual(post.call_count, 2)
        self.assertNotEqual(post.call_args_list[0].args[0], post.call_args_list[1].args[0])

    @patch("words.gemini_service.requests.post")
    def test_persistent_server_failure_stops(self, post):
        post.return_value = self.response(503)
        with self.assertRaises(GeminiError) as error:
            generate_word_info("hello")
        self.assertEqual(error.exception.status_code, 503)
        self.assertEqual(post.call_count, 2)

    @patch("words.gemini_service.requests.post")
    def test_client_errors_exhaust_fallbacks(self, post):
        for status, attempts in [(429, 4), (403, 4), (404, 2), (400, 4)]:
            with self.subTest(status=status):
                post.reset_mock()
                post.return_value = self.response(status)
                with self.assertRaises(GeminiError):
                    generate_word_info("hello")
                self.assertEqual(post.call_count, attempts)

    @patch("words.gemini_service.requests.post")
    def test_timeout_is_sanitized_after_fallbacks(self, post):
        post.side_effect = requests.Timeout("secret-request-details")
        with self.assertRaises(GeminiError) as error:
            generate_word_info("hello")
        self.assertEqual(error.exception.status_code, 504)
        self.assertNotIn("secret", str(error.exception))
        self.assertEqual(post.call_count, 4)

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

    @override_settings(GEMINI_MODELS=["gemini-3.6-flash"])
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
