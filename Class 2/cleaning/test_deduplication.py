#!/usr/bin/env python3
"""
Test script to demonstrate the deduplication system with sample duplicate content.
"""

import os
import tempfile
import shutil
from pathlib import Path
from text_deduplicator import TextDeduplicator

def create_test_files():
    """Create test files with some duplicates to demonstrate the system."""
    
    # Create test directory structure
    test_dir = Path("cleaning/test_input")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample content
    content1 = """
    Electric Service Requirements Manual
    This document outlines the requirements for electric service installation.
    All installations must comply with safety standards and local regulations.
    Proper grounding and circuit protection are essential for safe operation.
    """
    
    content2 = """
    Electric Service Requirements Manual
    This document outlines the requirements for electric service installation.
    All installations must comply with safety standards and local regulations.
    Proper grounding and circuit protection are essential for safe operation.
    Additional requirements may apply based on local codes.
    """
    
    content3 = """
    Underground Conduit Specifications
    This specification covers the requirements for underground conduit systems.
    All conduits must be properly sealed and protected from moisture.
    Installation depth must meet local code requirements.
    """
    
    content4 = """
    Underground Conduit Specifications
    This specification covers the requirements for underground conduit systems.
    All conduits must be properly sealed and protected from moisture.
    Installation depth must meet local code requirements.
    Material specifications are detailed in section 3.2.
    """
    
    content5 = """
    Completely Different Document
    This is a unique document with different content.
    It should not be considered a duplicate of any other file.
    """
    
    # Create test files
    test_files = [
        ("file1.txt", content1),
        ("file2.txt", content2),  # Similar to file1
        ("file3.txt", content3),
        ("file4.txt", content4),  # Similar to file3
        ("file5.txt", content5),  # Unique
        ("subfolder/file6.txt", content1),  # Duplicate of file1
        ("subfolder/file7.txt", content3),  # Duplicate of file3
    ]
    
    for filename, content in test_files:
        file_path = test_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Created {len(test_files)} test files in {test_dir}")
    return test_dir

def run_test():
    """Run the deduplication test."""
    
    # Create test files
    test_input = create_test_files()
    test_output = Path("cleaning/test_output")
    
    # Run deduplication
    print("\nRunning deduplication test...")
    deduplicator = TextDeduplicator(
        input_dir=str(test_input),
        output_dir=str(test_output),
        similarity_threshold=0.7
    )
    deduplicator.process_files()
    
    # Show results
    print(f"\nTest completed!")
    print(f"Input files: {len(list(test_input.rglob('*.txt')))}")
    print(f"Output files: {len(list(test_output.rglob('*.txt')))}")
    
    # Check if stats file was created
    stats_file = test_output / "stats.md"
    if stats_file.exists():
        print(f"\nStatistics file created: {stats_file}")
        with open(stats_file, 'r') as f:
            print(f.read())
    else:
        print("\nNo duplicates found in test data")

def cleanup_test():
    """Clean up test files."""
    test_dirs = ["cleaning/test_input", "cleaning/test_output"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"Cleaned up {test_dir}")

if __name__ == "__main__":
    print("Text Deduplication Test")
    print("=" * 30)
    
    try:
        run_test()
    finally:
        # Uncomment the next line to automatically clean up test files
        # cleanup_test()
        pass 