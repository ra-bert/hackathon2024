import unittest
from mock import MagicMock
from anomalies import embedding
import pandas as pd


class TestEmbedding(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.er = embedding.EmbeddingRequester(self.client, model="test")

    def test_df_embeddings(self):
        df = pd.DataFrame(
            {"f_name": ["a", "b"], "text": ["hello world", "goodbye world"]}
        )
        self.client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[1, 2, 3])], usage=MagicMock(prompt_tokens=2)
        )
        new_df = self.er.embed_df(df)
        self.assertEqual(new_df.shape, (2, 3))
        self.assertEqual(new_df["embedding"].tolist(), [[1, 2, 3], [1, 2, 3]])
        self.assertEqual(self.er.tokens, 4)
        self.assertLess(self.er.total_cost, 1)
