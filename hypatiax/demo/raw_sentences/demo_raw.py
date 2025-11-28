#!/usr/bin/env python3
"""
Demo Raw Sentences
Sample sentences for testing HypatiaX demos
"""

# Mathematical queries
MATH_QUERIES = [
    "calculate the area of a circle with radius 5",
    "what is 2 + 2",
    "find the square root of 16",
    "what is 15% of 200",
    "solve for x: 2x + 5 = 15",
]

# Conversion queries
CONVERSION_QUERIES = [
    "convert 100 celsius to fahrenheit",
    "how many meters in 5 kilometers",
    "convert 10 pounds to kilograms",
    "what is 5 feet in centimeters",
    "convert 2 hours to minutes",
]

# Information queries
INFO_QUERIES = [
    "what is the capital of France",
    "who wrote Romeo and Juliet",
    "when was the first computer invented",
    "what is the speed of light",
    "how many planets are in the solar system",
]

# Command queries
COMMAND_QUERIES = [
    "set a timer for 5 minutes",
    "remind me to call John at 3pm",
    "create a note titled 'grocery list'",
    "delete my last reminder",
    "show me today's schedule",
]

# Complex queries
COMPLEX_QUERIES = [
    "if I drive 60 miles per hour for 2.5 hours, how far will I go",
    "calculate the compound interest on $1000 at 5% for 3 years",
    "what is the area of a rectangle with length 8 and width 5",
    "find the average of 10, 20, 30, 40, and 50",
    "if a shirt costs $25 and is 20% off, what is the final price",
]

# All demo sentences combined
ALL_DEMO_SENTENCES = (
    MATH_QUERIES +
    CONVERSION_QUERIES +
    INFO_QUERIES +
    COMMAND_QUERIES +
    COMPLEX_QUERIES
)

# Sample training data format
SAMPLE_TRAINING_DATA = [
    {
        "text": "calculate the area of a circle with radius 5",
        "intent": "MATH_CALCULATION",
        "entities": [
            {"text": "area", "type": "OPERATION", "start
