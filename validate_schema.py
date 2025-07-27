#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1A
Standalone Schema Validation Tool 🛠️

This script validates Challenge 1A output files against the official schema.
It checks JSON files in a specified directory to ensure they conform to the expected structure.
"""

import json
import sys
from pathlib import Path

def colored_text(text: str, color_code: str) -> str:
    """
    Return colored text for terminal output using ANSI escape codes.

    Args:
        text: The text to be colored.
        color_code: ANSI color code to apply to the text.

    Returns:
        String with ANSI color codes applied for terminal output.
    """
    return f"\033[{color_code}m{text}\033[0m"

def print_header(text: str) -> None:
    """
    Prints a formatted header with decorative elements.

    Args:
        text: The header text to display.
    """
    print("\n" + "✨" * 50)
    print(f"🌟 {text}")
    print("✨" * 50 + "\n")

def print_error(message: str) -> None:
    """
    Prints an error message with decorative elements.

    Args:
        message: The error message to display.
    """
    print(f"❌ {colored_text(message, '31')}")

def print_info(message: str) -> None:
    """
    Prints an informational message.

    Args:
        message: The informational message to display.
    """
    print(f"ℹ️ {message}")

def main():
    """
    Main validation function.

    This function initializes the validation process, checks for the existence of the output directory,
    and validates all JSON files found within it.
    """

    print_header("Challenge 1A Schema Validation Tool")

    # Define the output directory path
    output_dir = Path("output")

    # Check if the output directory exists
    if not output_dir.exists():
        print_error("Output directory not found!")
        print_info("Please ensure you have an 'output' directory with JSON files.")
        sys.exit(1)

    try:
        # Attempt to import the SchemaValidator and related functions
        from src.validate_schema import SchemaValidator, validate_output_directory
    except ImportError:
        # Handle import errors gracefully
        print_error("Error: Could not import schema_validator module")
        print_info("Make sure you're running this from the Challenge_1a directory")
        sys.exit(1)

    # Validate all files in the output directory
    print_info("Starting validation process...")
    validate_output_directory(output_dir)
    print_info("Validation process completed.")

if __name__ == "__main__":
    # Execute the main function when the script is run directly
    main()
