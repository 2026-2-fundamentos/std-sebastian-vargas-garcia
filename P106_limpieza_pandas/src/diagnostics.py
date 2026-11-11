from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = ACTIVITY_DIR / "data" / "ventas.csv"
OUTPUT_FILE = ACTIVITY_DIR / "submission" / "ventas.csv"


def main():
    df = pd.read_csv(OUTPUT_FILE)
    series = df["contact_email"]
    series = series.drop_duplicates()
    series = series.sort_values(ascending=True)

    d = {}
    for value in series:
        key = str(value)
        key = key.lower()
        key = key.replace("  ", " ")
        if key in d:
            d[key].append(value)
            d[key] = list(set(d[key]))
        else:
            d[key] = [value]

    for key, values in d.items():
        if len(values) > 1:
            print(f"{key}")
            for v in values:
                print(f"    {v}")

    for value in series:
       print(repr(value))


if __name__ == "__main__":
    main()