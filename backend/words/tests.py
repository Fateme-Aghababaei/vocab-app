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