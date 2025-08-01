# PDF to Text OCR Batch Converter

A comprehensive batch OCR system that converts PDFs to text while retaining layout using Tesseract OCR with PSM 1 mode.

## Features

- **Recursive Processing**: Automatically processes all PDFs in subdirectories
- **Layout Retention**: Uses Tesseract PSM 1 mode to preserve text layout
- **High Quality**: 300 DPI (Industry standard for balancing accuracy and computation)
- **Folder Structure**: Maintains exact folder hierarchy from input to output
- **UTF-8 Support**: Proper encoding for international characters

### Install System Dependencies

#### macOS:
```bash
# Install Tesseract OCR
brew install tesseract

# Install Poppler (for PDF processing)
brew install poppler

# Install from requirements file
pip install -r requirements_ocr.txt
```


#### Custom Directories:
```bash
python batch_ocr.py --pdf-dir pdf_ocr --txt-dir txt_ocr
```

### Tesseract Settings

The script uses the following Tesseract configuration:
- **PSM 1**: Automatic page segmentation with OSD (Orientation and Script Detection)
    '--psm 6'  # Uniform block of text
    '--psm 3'  # Fully automatic page segmentation
    '--psm 0'  # Orientation and script detection only    
- **OEM 3**: Default OCR Engine Mode, LSTM ()


## Output Format

Each PDF is converted to a text file with the following format:

```
=== PAGE 1 ===
[Extracted text from page 1]

=== PAGE 2 ===
[Extracted text from page 2]

...
```

