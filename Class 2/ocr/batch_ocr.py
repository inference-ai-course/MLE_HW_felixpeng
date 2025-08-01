#!/usr/bin/env python3
"""
Batch PDF to Text OCR Converter
Converts PDFs to text using Tesseract OCR while retaining layout (PSM 1)
Maintains folder structure from pdf_ocr to txt_ocr
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Tuple
import argparse

# OCR and PDF processing libraries
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_batch.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BatchOCRConverter:
    def __init__(self, pdf_dir: str = "pdf_ocr", txt_dir: str = "txt_ocr"):
        """
        Initialize the batch OCR converter
        
        Args:
            pdf_dir: Directory containing PDF files
            txt_dir: Directory to output text files
        """
        self.pdf_dir = Path(pdf_dir)
        self.txt_dir = Path(txt_dir)
        
        # Ensure output directory exists
        self.txt_dir.mkdir(exist_ok=True)
        
        # Tesseract configuration for layout retention
        self.tesseract_config = '--psm 1 --oem 3'
        
        logger.info(f"Initialized BatchOCRConverter")
        logger.info(f"PDF directory: {self.pdf_dir}")
        logger.info(f"Text output directory: {self.txt_dir}")
    
    def find_pdf_files(self) -> List[Path]:
        """
        Recursively find all PDF files in the pdf_dir
        
        Returns:
            List of PDF file paths
        """
        pdf_files = []
        if self.pdf_dir.exists():
            for pdf_file in self.pdf_dir.rglob("*.pdf"):
                pdf_files.append(pdf_file)
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def get_relative_path(self, pdf_path: Path) -> Path:
        """
        Get the relative path from pdf_dir to maintain folder structure
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Relative path from pdf_dir
        """
        return pdf_path.relative_to(self.pdf_dir)
    
    def get_output_path(self, pdf_path: Path) -> Path:
        """
        Generate output text file path maintaining folder structure
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Path for output text file
        """
        relative_path = self.get_relative_path(pdf_path)
        # Change extension from .pdf to .txt
        txt_filename = relative_path.with_suffix('.txt')
        output_path = self.txt_dir / txt_filename
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
    def convert_pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """
        Convert PDF to list of PIL Images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Image objects
        """
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF to images with high DPI for better OCR
            images = convert_from_path(
                pdf_path,
                dpi=300,  # High DPI for better OCR accuracy
                fmt='PNG',
                thread_count=4  # Use multiple threads for faster processing
            )
            
            logger.info(f"Converted {len(images)} pages to images")
            return images
            
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path}: {str(e)}")
            return []
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from a single image using Tesseract
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text string
        """
        try:
            # Use Tesseract with PSM 1 for layout retention
            text = pytesseract.image_to_string(
                image,
                config=self.tesseract_config,
                lang='eng'  # English language
            )
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def process_single_pdf(self, pdf_path: Path) -> bool:
        """
        Process a single PDF file and save text output
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get output path
            output_path = self.get_output_path(pdf_path)
            
            # Skip if output already exists (uncomment to enable)
            # if output_path.exists():
            #     logger.info(f"Skipping {pdf_path} - output already exists")
            #     return True
            
            logger.info(f"Processing: {pdf_path}")
            logger.info(f"Output: {output_path}")
            
            # Convert PDF to images
            images = self.convert_pdf_to_images(pdf_path)
            if not images:
                logger.error(f"No images extracted from {pdf_path}")
                return False
            
            # Extract text from each page
            all_text = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                page_text = self.extract_text_from_image(image)
                all_text.append(f"=== PAGE {i+1} ===\n{page_text}\n")
            
            # Combine all text
            full_text = "\n".join(all_text)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            logger.info(f"Successfully processed {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return False
    
    def run_batch_conversion(self) -> Tuple[int, int]:
        """
        Run batch conversion of all PDF files
        
        Returns:
            Tuple of (successful_conversions, total_files)
        """
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found")
            return 0, 0
        
        successful = 0
        total = len(pdf_files)
        
        logger.info(f"Starting batch conversion of {total} PDF files")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Processing file {i}/{total}: {pdf_file.name}")
            
            if self.process_single_pdf(pdf_file):
                successful += 1
            else:
                logger.error(f"Failed to process {pdf_file}")
        
        logger.info(f"Batch conversion complete: {successful}/{total} files processed successfully")
        return successful, total

def main():
    """Main function to run the batch OCR converter"""
    parser = argparse.ArgumentParser(description='Batch PDF to Text OCR Converter')
    parser.add_argument('--pdf-dir', default='pdf_ocr', help='Directory containing PDF files')
    parser.add_argument('--txt-dir', default='txt_ocr', help='Directory to output text files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize converter
    converter = BatchOCRConverter(args.pdf_dir, args.txt_dir)
    
    # Run batch conversion
    successful, total = converter.run_batch_conversion()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"BATCH OCR CONVERSION SUMMARY")
    print(f"{'='*50}")
    print(f"Total PDF files found: {total}")
    print(f"Successfully converted: {successful}")
    print(f"Failed conversions: {total - successful}")
    print(f"Success rate: {(successful/total)*100:.1f}%" if total > 0 else "No files processed")
    print(f"{'='*50}")
    
    if successful == total:
        print("✅ All files processed successfully!")
    else:
        print("⚠️  Some files failed to process. Check the log for details.")

if __name__ == "__main__":
    main() 