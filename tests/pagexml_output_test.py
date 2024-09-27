import unittest
import pandas as pd
import os

filename = "data/pagexmls.csv"


@unittest.skipIf(not os.path.exists(filename), "No pagexmls present not found")
class TestEmbedding(unittest.TestCase):
    def test_stuff(self):
        df = pd.read_csv(filename)
        print(df.columns)
        self.assertTrue("text" in df.columns)

        texts = df["text"].tolist()
        cleaned = [text for text in texts if isinstance(text, str) and text.strip()]
        print(f"Texts: {len(texts)}, Cleaned: {len(cleaned)}")
        wcs = [len(text.strip().split(" ")) for text in cleaned]
        print(
            f"total words: {sum(wcs)}, avg words: {sum(wcs) / len(wcs)}, min words: {min(wcs)}, max words: {max(wcs)}"
        )

        self.assertAlmostEqual(
            len(df), 2500, delta=100, msg="should be around 2500 rows"
        )
        self.assertLess(
            len(texts) - len(cleaned), 120, msg="should be less than 120 empty docs"
        )
        self.assertLess(max(wcs), 1500, msg="should be less than 1500 words per doc")
        self.assertLess(
            sum(wcs) / len(wcs), 500, msg="should be less than 500 words avg"
        )
