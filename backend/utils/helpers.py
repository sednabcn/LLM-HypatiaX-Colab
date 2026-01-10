"""
Helper Utilities and Common Functions
File: backend/utils/helpers.py
"""

import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Union

# ============================================================================
# VALIDATION HELPERS
# ============================================================================


def validate_required_fields(
    data: Dict, required_fields: List[str]
) -> tuple[bool, Optional[str]]:
    """
    Validate that required fields are present in data

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing = [field for field in required_fields if field not in data]

    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    return True, None


def validate_numeric(
    value: Any, field_name: str, min_val: float = None, max_val: float = None
) -> tuple[bool, Optional[str]]:
    """
    Validate numeric value

    Args:
        value: Value to validate
        field_name: Name of the field
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num = float(value)

        if min_val is not None and num < min_val:
            return False, f"{field_name} must be >= {min_val}"

        if max_val is not None and num > max_val:
            return False, f"{field_name} must be <= {max_val}"

        return True, None

    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"


def validate_string(
    value: Any, field_name: str, min_length: int = None, max_length: int = None
) -> tuple[bool, Optional[str]]:
    """
    Validate string value

    Args:
        value: Value to validate
        field_name: Name of the field
        min_length: Minimum string length
        max_length: Maximum string length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"

    if min_length is not None and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"

    if max_length is not None and len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"

    return True, None


# ============================================================================
# TEXT PROCESSING HELPERS
# ============================================================================


def clean_text(text: str) -> str:
    """
    Clean and normalize text

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from text

    Args:
        text: Input text

    Returns:
        List of numbers
    """
    pattern = r"-?\d+\.?\d*"
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case to camelCase

    Args:
        snake_str: Snake case string

    Returns:
        Camel case string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convert camelCase to snake_case

    Args:
        camel_str: Camel case string

    Returns:
        Snake case string
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


# ============================================================================
# DATA FORMATTING HELPERS
# ============================================================================


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format number as currency

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted currency string
    """
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}

    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with thousand separators

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted number string
    """
    return f"{value:,.{decimals}f}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(
    date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse datetime string

    Args:
        date_str: Date string
        format_str: Format string

    Returns:
        Datetime object or None
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


# ============================================================================
# TIMING AND PERFORMANCE HELPERS
# ============================================================================


def timing_decorator(func):
    """
    Decorator to measure function execution time

    Args:
        func: Function to time

    Returns:
        Wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to ms

        print(f"{func.__name__} took {duration:.2f}ms")
        return result

    return wrapper


class Timer:
    """Context manager for timing code blocks"""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        duration = (self.end_time - self.start_time) * 1000
        print(f"{self.name} took {duration:.2f}ms")

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


# ============================================================================
# CACHING HELPERS
# ============================================================================


def simple_cache(maxsize: int = 128, ttl: int = 3600):
    """
    Simple cache decorator with TTL (time to live)

    Args:
        maxsize: Maximum cache size
        ttl: Time to live in seconds

    Returns:
        Decorator function
    """
    cache = {}
    timestamps = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(kwargs)
            current_time = time.time()

            # Check if cached and not expired
            if key in cache and key in timestamps:
                if current_time - timestamps[key] < ttl:
                    return cache[key]

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = current_time

            # Cleanup old entries if cache is full
            if len(cache) > maxsize:
                oldest_key = min(timestamps.keys(), key=lambda k: timestamps[k])
                del cache[oldest_key]
                del timestamps[oldest_key]

            return result

        return wrapper

    return decorator


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


# ============================================================================
# FILE HELPERS
# ============================================================================


def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if not

    Args:
        path: Directory path

    Returns:
        True if directory exists or was created
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False


def read_json_file(filepath: str) -> Optional[Dict]:
    """
    Read JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary or None if error
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {filepath}: {e}")
        return None


def write_json_file(filepath: str, data: Dict, indent: int = 2) -> bool:
    """
    Write data to JSON file

    Args:
        filepath: Path to JSON file
        data: Data to write
        indent: JSON indentation

    Returns:
        True if successful
    """
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"Error writing JSON file {filepath}: {e}")
        return False


def get_file_size(filepath: str) -> Optional[int]:
    """
    Get file size in bytes

    Args:
        filepath: Path to file

    Returns:
        File size or None if error
    """
    try:
        return os.path.getsize(filepath)
    except Exception as e:
        print(f"Error getting file size {filepath}: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


# ============================================================================
# API RESPONSE HELPERS
# ============================================================================


def success_response(data: Any, message: str = None, meta: Dict = None) -> Dict:
    """
    Create success API response

    Args:
        data: Response data
        message: Optional message
        meta: Optional metadata

    Returns:
        Response dictionary
    """
    response = {"success": True, "data": data}

    if message:
        response["message"] = message

    if meta:
        response["meta"] = meta

    return response


def error_response(error: str, code: int = None, details: Any = None) -> Dict:
    """
    Create error API response

    Args:
        error: Error message
        code: Optional error code
        details: Optional error details

    Returns:
        Response dictionary
    """
    response = {"success": False, "error": error}

    if code:
        response["code"] = code

    if details:
        response["details"] = details

    return response


def paginate_response(items: List, page: int, per_page: int, total: int) -> Dict:
    """
    Create paginated API response

    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items

    Returns:
        Response dictionary with pagination metadata
    """
    total_pages = (total + per_page - 1) // per_page

    return {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


# ============================================================================
# MATH AND CALCULATION HELPERS
# ============================================================================


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division that handles division by zero

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def round_to_nearest(value: float, nearest: float = 0.01) -> float:
    """
    Round to nearest specified value

    Args:
        value: Value to round
        nearest: Round to nearest this value

    Returns:
        Rounded value
    """
    return round(value / nearest) * nearest


# ============================================================================
# CONVERSION HELPERS
# ============================================================================


def dict_to_query_string(params: Dict) -> str:
    """
    Convert dictionary to URL query string

    Args:
        params: Dictionary of parameters

    Returns:
        Query string
    """
    return "&".join(f"{k}={v}" for k, v in params.items())


def query_string_to_dict(query_string: str) -> Dict:
    """
    Convert URL query string to dictionary

    Args:
        query_string: Query string

    Returns:
        Dictionary of parameters
    """
    if not query_string:
        return {}

    params = {}
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value

    return params


def flatten_dict(d: Dict, parent_key: str = "", sep: str = "_") -> Dict:
    """
    Flatten nested dictionary

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict, sep: str = "_") -> Dict:
    """
    Unflatten dictionary

    Args:
        d: Dictionary to unflatten
        sep: Separator used in keys

    Returns:
        Unflattened dictionary
    """
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


# ============================================================================
# RETRY HELPERS
# ============================================================================


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator with exponential backoff

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Backoff multiplier

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise

                    print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


# ============================================================================
# SANITIZATION HELPERS
# ============================================================================


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")

    return sanitized or "unnamed"


def sanitize_html(text: str) -> str:
    """
    Basic HTML sanitization (remove tags)

    Args:
        text: Text with potential HTML

    Returns:
        Sanitized text
    """
    # Remove HTML tags
    return re.sub(r"<[^>]+>", "", text)


def sanitize_sql(text: str) -> str:
    """
    Basic SQL injection prevention (escape quotes)

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Escape single quotes
    return text.replace("'", "''")


# ============================================================================
# COMPARISON HELPERS
# ============================================================================


def deep_compare(obj1: Any, obj2: Any) -> bool:
    """
    Deep comparison of two objects

    Args:
        obj1: First object
        obj2: Second object

    Returns:
        True if objects are equal
    """
    if type(obj1) != type(obj2):
        return False

    if isinstance(obj1, dict):
        if set(obj1.keys()) != set(obj2.keys()):
            return False
        return all(deep_compare(obj1[k], obj2[k]) for k in obj1.keys())

    if isinstance(obj1, (list, tuple)):
        if len(obj1) != len(obj2):
            return False
        return all(deep_compare(a, b) for a, b in zip(obj1, obj2))

    return obj1 == obj2


# ============================================================================
# BATCH PROCESSING HELPERS
# ============================================================================


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def batch_process(items: List, func, batch_size: int = 100) -> List:
    """
    Process items in batches

    Args:
        items: Items to process
        func: Function to apply to each batch
        batch_size: Size of each batch

    Returns:
        List of results
    """
    results = []
    chunks = chunk_list(items, batch_size)

    for i, chunk in enumerate(chunks):
        print(f"Processing batch {i + 1}/{len(chunks)}...")
        batch_result = func(chunk)
        results.extend(batch_result)

    return results


# ============================================================================
# ENCRYPTION HELPERS (Basic)
# ============================================================================


def generate_hash(text: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of text

    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hash string
    """
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    else:  # sha256
        return hashlib.sha256(text.encode()).hexdigest()


def generate_token(length: int = 32) -> str:
    """
    Generate random token

    Args:
        length: Length of token

    Returns:
        Random token string
    """
    import secrets

    return secrets.token_hex(length // 2)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("🧰 HypatiaX Helper Utilities\n")

    # Test validation
    print("Testing validation...")
    is_valid, error = validate_required_fields(
        {"name": "test", "age": 25}, ["name", "age", "email"]
    )
    print(f"Validation result: {is_valid}, Error: {error}")

    # Test text processing
    print("\nTesting text processing...")
    text = "  This   is   messy    text  "
    print(f"Cleaned: '{clean_text(text)}'")

    # Test formatting
    print("\nTesting formatting...")
    print(f"Currency: {format_currency(1234.56)}")
    print(f"Percentage: {format_percentage(45.678)}")
    print(f"Number: {format_number(1234567.89)}")

    # Test timing
    print("\nTesting timing...")
    with Timer("Test operation"):
        time.sleep(0.1)

    # Test caching
    print("\nTesting caching...")

    @simple_cache(maxsize=5, ttl=60)
    def expensive_operation(x):
        time.sleep(0.1)
        return x * 2

    start = time.time()
    result1 = expensive_operation(5)
    time1 = time.time() - start

    start = time.time()
    result2 = expensive_operation(5)  # Should be cached
    time2 = time.time() - start

    print(f"First call: {time1 * 1000:.2f}ms")
    print(f"Cached call: {time2 * 1000:.2f}ms (should be much faster)")

    # Test math helpers
    print("\nTesting math helpers...")
    print(f"Safe divide: {safe_divide(10, 0, default=999)}")
    print(f"Percentage change: {calculate_percentage_change(100, 150):.2f}%")
    print(f"Clamp: {clamp(150, 0, 100)}")

    print("\n✅ All helper tests complete!")
