#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1A
PDF Outline Extraction - Main Entry Point 🚀

This script processes all PDFs in the input directory and generates structured JSON outlines for each document.


To run, navigate to the correct directory (Round 1A Understand..) using `cd` and execute `docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none team_tech_pulse_solution_1:69`.
"""

import os
import sys
import time
from pathlib import Path
from src.process_pdf import PDFProcessor

def main():
    """
    Main entry point for PDF processing. 📄➡️📑
    This function orchestrates the extraction of outlines from PDF files and saves them as JSON.
    """

    # Start the timer and announce the beginning of the process
    print("🌟 Starting PDF outline extraction... 🌟")
    start_time = time.time()

    # Define input and output directories
    input_dir = Path("./input")
    output_dir = Path("./output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory set to: {output_dir.absolute()}")

    # Initialize PDF processor
    processor = PDFProcessor()
    print("🛠️ PDF Processor initialized and ready to go!")

    # Get all PDF files from input directory
    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("🔍 No PDF files found in the input directory. Please check your input folder.")
        return

    print(f"📄 Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"  📄 {pdf_file.name}")

    # Process each PDF file
    processed_count = 0
    for pdf_file in pdf_files:
        try:
            print(f"\n🔄 Processing: {pdf_file.name}...")

            # Extract outline from PDF
            result = processor.extract_outline(pdf_file)

            # Create output JSON file
            output_file = output_dir / f"{pdf_file.stem}.json"
            processor.save_result(result, output_file)

            print(f"✅ Successfully generated: {output_file.name}!")
            processed_count += 1

        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {str(e)}")
            # Continue processing other files
            continue

    # Summary
    total_time = time.time() - start_time
    print(f"\n{'=' * 50}")
    print("🎉 Processing complete! 🎉")
    print(f"📊 Files processed: {processed_count}/{len(pdf_files)}")
    print(f"⏱️ Total time taken: {total_time:.2f} seconds")
    print(f"⏱️ Average time per file: {total_time / len(pdf_files):.2f} seconds")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
