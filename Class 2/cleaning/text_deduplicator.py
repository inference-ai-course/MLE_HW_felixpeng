#!/usr/bin/env python3
"""
Text Deduplication using MinHash
Removes duplicate or highly similar text files using MinHash for efficient similarity detection.
"""

import os
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datasketch import MinHash, MinHashLSH
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deduplication.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TextDeduplicator:
    def __init__(self, input_dir: str, output_dir: str, similarity_threshold: float = 0.7):
        """
        Initialize the text deduplicator.
        
        Args:
            input_dir: Directory containing text files to deduplicate
            output_dir: Directory to save cleaned files
            similarity_threshold: Minimum similarity to consider files as duplicates (0.0-1.0)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.similarity_threshold = similarity_threshold
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'removed_files': 0,
            'total_tokens': 0,
            'removed_tokens': 0,
            'duplicate_groups': [],
            'file_sizes': {}
        }
        
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words, removing common stop words and punctuation.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        # Convert to lowercase and remove extra whitespace
        text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Remove punctuation and split into tokens
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        return tokens
    
    def create_minhash(self, tokens: List[str], num_perm: int = 128) -> MinHash:
        """
        Create a MinHash for a list of tokens.
        
        Args:
            tokens: List of tokens
            num_perm: Number of permutations for MinHash
            
        Returns:
            MinHash object
        """
        mh = MinHash(num_perm=num_perm)
        for token in tokens:
            mh.update(token.encode('utf-8'))
        return mh
    
    def calculate_similarity(self, mh1: MinHash, mh2: MinHash) -> float:
        """
        Calculate Jaccard similarity between two MinHashes.
        
        Args:
            mh1: First MinHash
            mh2: Second MinHash
            
        Returns:
            Similarity score (0.0-1.0)
        """
        return mh1.jaccard(mh2)
    
    def find_duplicates(self, file_data: Dict[str, Tuple[List[str], MinHash]]) -> List[List[str]]:
        """
        Find groups of duplicate files using MinHash LSH.
        
        Args:
            file_data: Dictionary mapping file paths to (tokens, minhash) tuples
            
        Returns:
            List of duplicate groups (each group is a list of file paths)
        """
        # Create LSH index
        lsh = MinHashLSH(threshold=self.similarity_threshold, num_perm=128)
        
        # Add all MinHashes to LSH
        for file_path, (tokens, mh) in file_data.items():
            lsh.insert(file_path, mh)
        
        # Find duplicate groups
        duplicate_groups = []
        processed_files = set()
        
        for file_path, (tokens, mh) in file_data.items():
            if file_path in processed_files:
                continue
                
            # Find similar files using LSH
            similar_files = lsh.query(mh)
            similar_files = [f for f in similar_files if f != file_path]
            
            if similar_files:
                # Verify similarity with exact calculation
                verified_similar = [file_path]
                for similar_file in similar_files:
                    if similar_file in file_data:
                        sim_score = self.calculate_similarity(mh, file_data[similar_file][1])
                        if sim_score >= self.similarity_threshold:
                            verified_similar.append(similar_file)
                
                if len(verified_similar) > 1:
                    duplicate_groups.append(verified_similar)
                    processed_files.update(verified_similar)
        
        return duplicate_groups
    
    def process_files(self) -> None:
        """
        Process all text files in the input directory and remove duplicates.
        """
        logger.info(f"Starting deduplication process...")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Similarity threshold: {self.similarity_threshold}")
        
        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all text files
        text_files = list(self.input_dir.rglob("*.txt"))
        self.stats['total_files'] = len(text_files)
        logger.info(f"Found {len(text_files)} text files to process")
        
        if not text_files:
            logger.warning("No text files found in input directory")
            return
        
        # Process files and create MinHashes
        file_data = {}
        for file_path in text_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Skip empty files
                if not text.strip():
                    continue
                
                tokens = self.tokenize_text(text)
                if not tokens:
                    continue
                
                mh = self.create_minhash(tokens)
                file_data[str(file_path)] = (tokens, mh)
                
                # Store file size info
                self.stats['file_sizes'][str(file_path)] = {
                    'size_bytes': len(text.encode('utf-8')),
                    'token_count': len(tokens),
                    'char_count': len(text)
                }
                self.stats['total_tokens'] += len(tokens)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        self.stats['processed_files'] = len(file_data)
        logger.info(f"Successfully processed {len(file_data)} files")
        
        # Find duplicates
        duplicate_groups = self.find_duplicates(file_data)
        self.stats['duplicate_groups'] = duplicate_groups
        
        # Keep track of files to remove
        files_to_remove = set()
        for group in duplicate_groups:
            # Keep the first file, remove the rest
            files_to_remove.update(group[1:])
            for file_path in group[1:]:
                if file_path in self.stats['file_sizes']:
                    self.stats['removed_tokens'] += self.stats['file_sizes'][file_path]['token_count']
        
        self.stats['removed_files'] = len(files_to_remove)
        
        # Copy files to output directory, excluding duplicates
        copied_files = 0
        for file_path in file_data.keys():
            if file_path not in files_to_remove:
                try:
                    # Calculate relative path from input directory
                    rel_path = Path(file_path).relative_to(self.input_dir)
                    output_path = self.output_dir / rel_path
                    
                    # Create output directory if needed
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                        with open(output_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    
                    copied_files += 1
                    
                except Exception as e:
                    logger.error(f"Error copying {file_path}: {e}")
        
        logger.info(f"Copied {copied_files} files to output directory")
        logger.info(f"Removed {len(files_to_remove)} duplicate files")
        
        # Generate statistics
        self.generate_stats()
    
    def generate_stats(self) -> None:
        """
        Generate and save statistics about the deduplication process.
        """
        if self.stats['removed_files'] > 0:
            removal_percentage = (self.stats['removed_files'] / self.stats['total_files']) * 100
            token_removal_percentage = (self.stats['removed_tokens'] / self.stats['total_tokens']) * 100 if self.stats['total_tokens'] > 0 else 0
            
            stats_content = f"""# Text Deduplication Statistics

## Summary
- **Total files processed**: {self.stats['total_files']}
- **Files kept**: {self.stats['processed_files'] - self.stats['removed_files']}
- **Files removed**: {self.stats['removed_files']}
- **Removal percentage**: {removal_percentage:.2f}%

## Token Statistics
- **Total tokens**: {self.stats['total_tokens']:,}
- **Tokens removed**: {self.stats['removed_tokens']:,}
- **Token removal percentage**: {token_removal_percentage:.2f}%

## Duplicate Groups
Found {len(self.stats['duplicate_groups'])} groups of duplicate files:

"""
            
            for i, group in enumerate(self.stats['duplicate_groups'], 1):
                stats_content += f"### Group {i}\n"
                for file_path in group:
                    rel_path = Path(file_path).relative_to(self.input_dir)
                    file_info = self.stats['file_sizes'].get(file_path, {})
                    token_count = file_info.get('token_count', 0)
                    size_bytes = file_info.get('size_bytes', 0)
                    stats_content += f"- `{rel_path}` ({token_count:,} tokens, {size_bytes:,} bytes)\n"
                stats_content += "\n"
            
            # Save stats to output directory
            stats_file = self.output_dir / "stats.md"
            with open(stats_file, 'w', encoding='utf-8') as f:
                f.write(stats_content)
            
            logger.info(f"Statistics saved to {stats_file}")
        else:
            logger.info("No duplicates found - no statistics file created")

def main():
    """Main function to run the deduplication process."""
    input_dir = "ocr/txt_ocr"
    output_dir = "cleaning/txt_ocr_cleaned"
    similarity_threshold = 0.7
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        logger.error(f"Input directory {input_dir} does not exist")
        return
    
    # Create deduplicator and run
    deduplicator = TextDeduplicator(input_dir, output_dir, similarity_threshold)
    deduplicator.process_files()
    
    logger.info("Deduplication process completed!")

if __name__ == "__main__":
    main() 