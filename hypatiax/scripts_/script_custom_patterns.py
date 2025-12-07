import logging
import os

from hypatiax.patterns.custom_patterns import CustomPatterns

# Setup logging configuration
logging.basicConfig(level=logging.INFO)


def patterns_gen(domain, sub_domain, query_type, option):
    # Ensure option is meaningful
    valid_options = ["all", "default"]
    if option not in valid_options:
        logging.error(f"Invalid option '{option}'. Valid options are {valid_options}")
        return

    try:
        # Initialize the CustomPatterns class and fetch patterns
        patterns = CustomPatterns(domain, sub_domain, query_type)
        patterns.get_custom_patterns(option)
        logging.info(
            f"Pattern generation completed successfully for domain='{sub_domain}', query_type='{query_type}', option='{option}'."
        )
    except Exception as e:
        logging.error("Failed to generate patterns due to an error:", exc_info=True)


if __name__ == "__main__":
    # Example usage: generate all patterns for the 'queries' domain with description type
    patterns_gen("queries", "tableau", "desc", "all")
