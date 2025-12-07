# Batch Processing Demo

import pandas as pd
from demo.engine import HypatiaXEngine


def batch_demo(input_file: str, output_file: str):
    engine = HypatiaXEngine()

    # Read queries from file
    df = pd.read_csv(input_file)
    queries = df["query"].tolist()

    # Process all
    results = engine.batch_process(queries)

    # Save results
    engine.export_results(results, output_file, format="csv")

    print(f"Processed {len(results)} queries")
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    batch_demo("queries.csv", "results.csv")
