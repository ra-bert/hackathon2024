import pandas as pd
import argparse
from renumics import spotlight

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run spotlight on embeddings")
    parser.add_argument("--input-path", default="data/embeddings.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input_path)
    df = df[df["embedding"].str.len() > 5]
    print(df.head())
    spotlight.show(df, dtype={"embedding": spotlight.Embedding})
