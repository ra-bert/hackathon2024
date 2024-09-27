import pandas as pd
import argparse
from renumics import spotlight

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run spotlight on embeddings")
    parser.add_argument("-i", "--input-paths", action="append", default=[])
    args = parser.parse_args()

    df = pd.DataFrame()
    for path in args.input_paths:
        new_df = pd.read_csv(path)
        new_df = new_df[new_df["embedding"].str.len() > 5]
        print(f"loading {path} with {len(new_df)} rows")
        print(new_df.head())

        df = pd.concat([df, new_df])
    if len(df) == 0:
        raise RuntimeError(
            "You must provide at least one input path like '-i data/embeddings.csv'"
        )
    df.sample(frac=1).reset_index(drop=True)
    spotlight.show(df, dtype={"embedding": spotlight.Embedding})
