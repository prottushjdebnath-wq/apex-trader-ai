import pandas as pd


class SignalRanker:

    def score(self, df):

        scores = []

        for _, row in df.iterrows():

            volume_score = min(
                row["volume"] / 1_000_000,
                100
            )

            momentum_score = abs(
                row["change"]
            )

            total_score = (
                volume_score * 0.7
                + momentum_score * 0.3
            )

            scores.append(total_score)

        df["score"] = scores

        df = df.sort_values(
            by="score",
            ascending=False
        )

        return df


if __name__ == "__main__":

    sample = pd.DataFrame([
        {
            "symbol": "BTC",
            "volume": 50000000,
            "change": 3
        },
        {
            "symbol": "DOGE",
            "volume": 20000000,
            "change": 10
        }
    ])

    ranked = SignalRanker().score(sample)

    print(ranked)