from typing import Optional
from openai import OpenAI
import pandas as pd
import argparse
from tqdm import tqdm


# os.env OPENAI_API_KEY
class EmbeddingRequester(object):
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
        self.tokens = 0

    @staticmethod
    def create(model: str = "text-embedding-3-large"):
        return EmbeddingRequester(OpenAI(), model)

    def generate_embeddings(self, text: str):
        response = self.client.embeddings.create(model=self.model, input=text)
        self.tokens += response.usage.prompt_tokens
        return response.data[0].embedding

    def embed_df(
        self, df: pd.DataFrame, from_column: str = "text", to_column: str = "embedding"
    ):
        total = len(df)
        embeddings = []
        for _, row in tqdm(df.iterrows(), total=total):
            embeddings.append(self.generate_embeddings(row[from_column]))
        new_df = df.copy()
        new_df[to_column] = embeddings
        return new_df

    @property
    def total_cost(self):
        return self.tokens * 0.13 / 1e6

    def load_embed_and_save(
        self, input_path: str, output_path: str, max_rows: Optional[int] = None
    ):
        df = pd.read_csv(input_path)
        print(f"max lines {max_rows}")
        if max_rows and max_rows > 0:
            print("cropping")
            df = df.head(max_rows)
        new_df = self.embed_df(df)
        new_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="handle kfp pipelines")
    parser.add_argument("--max-lines", default="-1")
    parser.add_argument("--model", default="text-embedding-3-large")
    parser.add_argument("--input-path", default="data/pagexmls.csv")
    parser.add_argument("--output-path", default="data/embeddings.csv")
    args = parser.parse_args()

    er = EmbeddingRequester.create()
    er.load_embed_and_save(
        args.input_path, args.output_path, max_rows=int(args.max_lines)
    )
    print(f"Done. Tokens: {er.tokens} Total cost: {er.total_cost}")
