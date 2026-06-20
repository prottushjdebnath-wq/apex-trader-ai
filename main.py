from scanner.oi_rvol_scanner import OIRVOLScanner
from scanner.signal_ranker import SignalRanker


def main():

    scanner = OIRVOLScanner()

    df = scanner.scan()

    ranker = SignalRanker()

    ranked = ranker.score(df)

    print("\nTOP RANKED COINS\n")

    print(
        ranked[
            ["symbol", "volume", "change", "score"]
        ].head(10)
    )


if __name__ == "__main__":
    main()