# Text Deduplication System

This folder contains a text deduplication system that uses MinHash for efficient similarity detection and removes duplicate or highly similar text files.

## Overview

The system processes text files from the OCR output and removes duplicates based on content similarity using MinHash algorithms. It maintains the same folder structure as the input directory.

## Files

- `text_deduplicator.py` - Main deduplication script
- `deduplication.log` - Log file with processing details
- `txt_ocr_cleaned/` - Output directory with deduplicated files

## How it Works

### MinHash Algorithm
The system uses MinHash for efficient similarity detection:
1. **Tokenization**: Text is tokenized into words, removing stop words and punctuation
2. **MinHash Creation**: Each document's tokens are converted to a MinHash signature
3. **LSH (Locality Sensitive Hashing)**: Uses LSH to efficiently find similar documents
4. **Similarity Calculation**: Jaccard similarity is calculated between MinHashes
5. **Duplicate Removal**: Files with similarity ≥ 0.7 are considered duplicates

### Process Flow
1. **Input**: Reads all `.txt` files from `ocr/txt_ocr/`
2. **Processing**: Creates MinHashes for each file
3. **Detection**: Finds groups of similar files using LSH
4. **Filtering**: Removes duplicates while keeping the first occurrence
5. **Output**: Saves cleaned files to `txt_ocr_cleaned/` maintaining folder structure

## Configuration

- **Similarity Threshold**: 0.7 (70% similarity required for duplicate detection)
- **MinHash Permutations**: 128 (affects accuracy vs speed trade-off)
- **Stop Words**: Common English stop words are filtered out
- **Token Filtering**: Only tokens with length > 2 are considered

## Results

### Current Run Results
- **Total files processed**: 9
- **Files kept**: 9
- **Files removed**: 0
- **Removal percentage**: 0.00%

### Analysis
No duplicates were found in the current dataset, which suggests:
1. The OCR files are sufficiently different in content
2. The similarity threshold (0.7) may be appropriate for this dataset
3. The documents represent distinct technical specifications and guidelines

## Usage

```bash
# Run the deduplication process
python cleaning/text_deduplicator.py

# Check the results
ls -la cleaning/txt_ocr_cleaned/

# View the log
cat cleaning/deduplication.log
```

## Output Structure

The cleaned files maintain the same directory structure as the input:
```
txt_ocr_cleaned/
├── Electric Service Requirements Manual.txt
├── ESR Add Ons/
│   ├── 2013_ESR_Manual_Page_2_44i.txt
│   ├── 2022_ESR_Manual_Page_2_22i.txt
│   ├── Design Guide-ESR Section 8i.txt
│   └── LADWP Smart Inverter Technical Requirements.txt
├── Extra Files/
│   ├── FY2015_16_Schedule_of_Charges_for_Energy_Facilities.txt
│   └── Rules Governing Water  Electric Service Oct 2008 reso 010 331  010 362  011 121  013 115  013 246  017 180  019 170 019 201  024 028 WEB 101623.txt
├── NEM Guidelines (with April 2021 technical modification) (1).txt
└── SPECS 104 Underground_Conduit_and_Substructures_Specification_104_Rev_11_04_2021_.txt
```

## Statistics

When duplicates are found, a `stats.md` file is automatically generated in the output directory containing:
- File count statistics
- Token count statistics
- Removal percentages
- Detailed list of duplicate groups

## Dependencies

- `datasketch` - For MinHash and LSH algorithms
- `numpy` - For numerical operations
- `scipy` - Required by datasketch

## Performance

The system is designed to handle large datasets efficiently:
- **Time Complexity**: O(n) for LSH-based similarity search
- **Space Complexity**: O(n) for storing MinHashes
- **Memory Usage**: Scales linearly with number of files and average file size

## Customization

You can modify the similarity threshold and other parameters in `text_deduplicator.py`:
- `similarity_threshold`: Adjust the minimum similarity for duplicate detection
- `num_perm`: Change the number of MinHash permutations (affects accuracy)
- `stop_words`: Modify the list of stop words to filter 