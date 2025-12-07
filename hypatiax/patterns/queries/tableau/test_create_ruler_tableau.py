import argparse
import logging
import os
import sys
from importlib import resources
from pathlib import Path

import pandas as pd
import spacy
from spacy import load as spacy_load

from hypatiax.patterns.queries.tableau.generation import Generation_custom_tableau_patterns

# Setup logging with more detail
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_and_validate_data(path_data):
    """Load Excel data and ensure all values are strings"""
    try:
        # Read Excel file
        if isinstance(path_data, (str, Path)):
            df = pd.read_excel(path_data)
        else:
            # Handle resource path
            with path_data.open("rb") as f:
                df = pd.read_excel(f)

        logger.info(f"Loaded data with shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")

        # Convert all columns to string type to prevent tokenization errors
        for col in df.columns:
            df[col] = df[col].astype(str)
            # Replace 'nan' string with empty string
            df[col] = df[col].replace("nan", "")

        # Remove empty rows
        df = df[df.apply(lambda x: x.str.strip().str.len().sum() > 0, axis=1)]

        logger.info(f"Data after cleaning: {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        raise


def patterns_rules(data, ind, type_pattern):
    """Generate patterns with proper error handling"""
    # Define stopwords for descriptions and formulas
    stopwords_desc = [
        "\\",
        "Iri",
        "Se",
        "C",
        "Sepal",
        "ica",
        "Length",
        "'s",
        ".",
        "'",
        "s",
        "a",
        "(",
        ")",
        "Petal",
        "Distinct",
        "Width",
        ",",
        "'",
        "[",
        "]",
    ]
    stopwords_formulas = [
        "\\",
        "Iri",
        "Se",
        "C",
        "Sepal",
        "ica",
        "Length",
        "'s",
        ".",
        "'",
        "s",
        "a",
        "(",
        ")",
        "Petal",
        "Distinct",
        "distinct",
        "Width",
        ",",
        "BY",
        "by",
        "from",
        "[",
        "]",
    ]

    # Select stopwords based on indicator
    stopword_map = {
        "B": list(set(stopwords_desc + stopwords_formulas)),  # Both
        "F": stopwords_formulas,  # Formulas
        "D": stopwords_desc,  # Descriptions
    }

    if ind not in stopword_map:
        logger.error(f"Invalid indicator '{ind}'. Must be 'D', 'F', or 'B'.")
        return None

    chosen_stopwords = stopword_map[ind]
    logger.info(f"Using {len(chosen_stopwords)} stopwords for indicator '{ind}'")

    try:
        # Load and validate data
        if isinstance(data, (str, Path)) or hasattr(data, "open"):
            df = load_and_validate_data(data)
        else:
            df = data

        # Create generator
        generator = Generation_custom_tableau_patterns(df, chosen_stopwords)

        # Generate patterns
        result = generator.create_ruler_tableau(nlp, type_pattern)
        logger.info(f"Successfully generated patterns of type '{type_pattern}'")

        return result

    except Exception as e:
        logger.error(f"Error in patterns_rules: {e}", exc_info=True)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate query patterns for Tableau.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_create_ruler_tableau.py desc
  python test_create_ruler_tableau.py formulas
  python test_create_ruler_tableau.py both

  # With custom data file
  python test_create_ruler_tableau.py desc --data-file custom_formulas.xlsx
        """,
    )

    parser.add_argument("type", choices=["desc", "formulas", "both"], help="Type of patterns to generate")

    parser.add_argument("--data-file", type=str, default=None, help="Path to custom Excel data file (optional)")

    parser.add_argument(
        "--indicator",
        type=str,
        choices=["D", "F", "B"],
        default="B",
        help="Stopword indicator: S=descriptions, F=formulas, B=both (default: B)",
    )

    parser.add_argument("--output", type=str, default=None, help="Output file path for generated patterns (optional)")

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize spaCy model
        global nlp
        logger.info("Loading spaCy model 'en_core_web_sm'...")
        nlp = spacy_load("en_core_web_sm")
        logger.info("spaCy model loaded successfully")

        # Determine data path
        if args.data_file:
            # Use custom data file
            path_data = Path(args.data_file)
            if not path_data.exists():
                logger.error(f"Data file {path_data} does not exist.")
                sys.exit(1)
            logger.info(f"Using custom data file: {path_data}")
        else:
            # Use default resource path
            try:
                path_data = resources.files("hypatiax.datasets.queries.tableau.training").joinpath("formulas.xlsx")

                if not path_data.exists():
                    logger.error(f"Default data file not found at {path_data}")
                    logger.info("Try specifying a custom file with --data-file")
                    sys.exit(1)

                logger.info(f"Using default data file: {path_data}")
            except Exception as e:
                logger.error(f"Error accessing default data file: {e}")
                logger.info("Try specifying a custom file with --data-file")
                sys.exit(1)

        # Generate patterns
        logger.info(f"Generating '{args.type}' patterns with indicator '{args.indicator}'...")
        result = patterns_rules(path_data, args.indicator, args.type)

        if result is not None:
            logger.info("Pattern generation completed successfully")

            # Save output if specified
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save based on result type
                if isinstance(result, pd.DataFrame):
                    result.to_csv(output_path, index=False)
                    logger.info(f"Results saved to {output_path}")
                else:
                    import json

                    with open(output_path, "w") as f:
                        json.dump(result, f, indent=2)
                    logger.info(f"Results saved to {output_path}")
            else:
                logger.info("No output file specified. Results not saved.")
                logger.info(f"Result type: {type(result)}")
                if hasattr(result, "shape"):
                    logger.info(f"Result shape: {result.shape}")
        else:
            logger.error("Pattern generation failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("An error occurred:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
