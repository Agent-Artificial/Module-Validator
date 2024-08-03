import unittest
from ..embedding import EmbeddingModule


class TestEmbeddingModule(unittest.TestCase):
    def setUp(self):
        self.module = EmbeddingModule()

    def test_process(self):
        result = self.module.process("hello world")
        self.assertEqual(result, [15339, 1917])

    def test_token_usage(self):
        # Assuming process() updates token_usage
        self.module.process("hello world")
        token_usage = self.module.token_usage.model_dump()
        self.assertEqual(token_usage, {'total_tokens': 2, 'prompt_tokens': 2, 'request_tokens': 2, 'response_tokens': 0})

    def test_cosine_similarity_different_vectors(self):
        result = self.module.cosine_similarity([1, 2, 3], [0.0004, 0.0005, 0.000006])
        self.assertAlmostEqual(result, 0.5918357821669399, places=7)

    def test_cosine_similarity_identical_vectors(self):
        result = self.module.cosine_similarity([1, 2, 3], [1, 2, 3])
        self.assertEqual(result, 1.0)

if __name__ == '__main__':
    unittest.main()