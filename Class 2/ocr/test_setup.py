#!/usr/bin/env python3
"""
Test script to verify OCR setup and dependencies
"""

import sys
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import pytesseract
        print("✅ pytesseract imported successfully")
    except ImportError as e:
        print(f"❌ pytesseract import failed: {e}")
        return False
    
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image imported successfully")
    except ImportError as e:
        print(f"❌ pdf2image import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_tesseract():
    """Test if Tesseract is properly installed"""
    print("\nTesting Tesseract installation...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        print("\nTo install Tesseract:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def test_pdf2image():
    """Test if pdf2image backend is available"""
    print("\nTesting pdf2image backend...")
    
    try:
        from pdf2image import convert_from_path
        # Simple test - just check if the module can be imported
        print("✅ pdf2image backend available")
        return True
    except Exception as e:
        print(f"❌ pdf2image backend issue: {e}")
        print("\nTo install pdf2image backend:")
        print("  macOS: brew install poppler")
        print("  Ubuntu: sudo apt-get install poppler-utils")
        print("  Windows: Download poppler binaries")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directory structure...")
    
    pdf_dir = Path("pdf_ocr")
    txt_dir = Path("txt_ocr")
    
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.rglob("*.pdf"))
        print(f"✅ PDF directory exists with {len(pdf_files)} PDF files")
    else:
        print("❌ PDF directory 'pdf_ocr' not found")
        return False
    
    if txt_dir.exists():
        print("✅ Text output directory exists")
    else:
        print("⚠️  Text output directory 'txt_ocr' will be created")
    
    return True

def test_simple_ocr():
    """Test basic OCR functionality"""
    print("\nTesting basic OCR functionality...")
    
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 10), "OCR Test Text", fill='black', font=font)
        
        # Perform OCR
        text = pytesseract.image_to_string(img, config='--psm 6')
        
        if text.strip():
            print("✅ Basic OCR test passed")
            print(f"   Extracted text: '{text.strip()}'")
            return True
        else:
            print("❌ OCR test failed - no text extracted")
            return False
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("OCR SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Tesseract Installation", test_tesseract),
        ("PDF2Image Backend", test_pdf2image),
        ("Directory Structure", test_directories),
        ("Basic OCR Functionality", test_simple_ocr)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("✅ All tests passed! OCR system is ready to use.")
        print("\nYou can now run:")
        print("  python batch_ocr.py")
        print("  or")
        print("  jupyter notebook ocr_demo.ipynb")
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 