"""
Adobe India Hackathon 2025 - Challenge 1A
Utility Classes - Font analysis and text processing utilities

This module provides utility classes for analyzing font characteristics and processing text
to identify document structure and content characteristics.
"""

import re
from typing import Dict, List, Any, Set, Tuple

class FontAnalyzer:
    """Analyzes font characteristics to identify document structure."""

    def __init__(self):
        """Initialize the font analyzer with a cache for storing font data."""
        self.font_cache = {}

    def analyze_font_distribution(self, text_dict: Dict) -> Dict[str, Any]:
        """
        Analyze the distribution of fonts in a document.

        This method processes a text dictionary from a PDF to extract font sizes, names, and flags,
        and calculates average, maximum, and minimum font sizes.

        Args:
            text_dict: A dictionary containing text data from PyMuPDF.

        Returns:
            Dictionary with font analysis results including sizes, names, flags, and statistics.
        """
        font_sizes = []
        font_names = []
        font_flags = []

        if 'blocks' not in text_dict:
            return {'sizes': [], 'names': [], 'flags': []}

        for block in text_dict['blocks']:
            if 'lines' not in block:
                continue

            for line in block['lines']:
                if 'spans' not in line:
                    continue

                for span in line['spans']:
                    font_sizes.append(span.get('size', 12))
                    font_names.append(span.get('font', 'default'))
                    font_flags.append(span.get('flags', 0))

        return {
            'sizes': font_sizes,
            'names': font_names,
            'flags': font_flags,
            'avg_size': sum(font_sizes) / len(font_sizes) if font_sizes else 12,
            'max_size': max(font_sizes) if font_sizes else 12,
            'min_size': min(font_sizes) if font_sizes else 12
        }

    def is_heading_font(self, font_size: float, font_flags: int, avg_size: float, threshold: float = 1.2) -> bool:
        """
        Determine if font characteristics suggest a heading.

        This method checks if a font is likely used for headings based on its size and boldness.

        Args:
            font_size: Font size of the text.
            font_flags: Font flags indicating style attributes like bold or italic.
            avg_size: Average font size in the document.
            threshold: Size threshold multiplier to determine if the font is large enough to be a heading.

        Returns:
            True if the font is likely a heading font.
        """
        # Check if the font size is significantly larger than the average
        size_ratio = font_size / avg_size if avg_size > 0 else 1
        is_large = size_ratio >= threshold

        # Check if the font is bold
        is_bold = bool(font_flags & 2**4)

        return is_large or is_bold

    def get_font_hierarchy(self, font_sizes: List[float]) -> Dict[float, int]:
        """
        Create a hierarchy mapping from font sizes.

        This method maps font sizes to hierarchy levels, which can be used to infer document structure.

        Args:
            font_sizes: List of font sizes found in the document.

        Returns:
            Dictionary mapping font size to hierarchy level (1=largest, 2=second, etc.).
        """
        unique_sizes = sorted(set(font_sizes), reverse=True)
        hierarchy = {}

        for i, size in enumerate(unique_sizes[:3]):  # Only consider top 3 levels
            hierarchy[size] = i + 1

        return hierarchy

class TextProcessor:
    """Processes and analyzes text content for structure detection."""

    def __init__(self):
        """Initialize the text processor with a set of stop words."""
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'then', 'once'
        }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        This method removes extra whitespace, control characters, and normalizes quotes and dashes.

        Args:
            text: Raw text string to clean.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        text = text.replace('–', '-').replace('—', '-')

        return text

    def is_likely_heading(self, text: str) -> bool:
        """
        Determine if text is likely a heading based on content analysis.

        This method checks for patterns and characteristics typical of headings.

        Args:
            text: Text to analyze.

        Returns:
            True if the text is likely a heading.
        """
        if not text or len(text.strip()) < 3:
            return False

        text = text.strip()

        # Check for common heading patterns
        heading_patterns = [
            r'^\d+\.',  # Numbered sections
            r'^[A-Z][A-Z\s]*$',  # ALL CAPS
            r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*$',  # Title Case
            r'^(Chapter|Section|Part)\s+\d+',  # Chapter/Section markers
        ]

        for pattern in heading_patterns:
            if re.match(pattern, text):
                return True

        # Check text characteristics
        words = text.split()

        # Reasonable length for headings
        if not (2 <= len(words) <= 12):
            return False

        # Should not end with sentence punctuation
        if text.endswith(('.', '!', '?')):
            return False

        # Should not be mostly stop words
        non_stop_words = [w for w in words if w.lower() not in self.stop_words]
        if len(non_stop_words) < len(words) * 0.5:
            return False

        return True

    def extract_numbering(self, text: str) -> Tuple[Any, str]:
        """
        Extract numbering information from heading text.

        This method identifies and extracts numbering patterns from text to infer hierarchy levels.

        Args:
            text: Heading text to analyze.

        Returns:
            Tuple of (level, clean_text) where level is the inferred hierarchy level.
        """
        # Pattern for multi-level numbering (e.g., 1.2.3)
        match = re.match(r'^(\d+(?:\.\d+)*)\.\s*(.+)$', text)
        if match:
            numbering = match.group(1)
            clean_text = match.group(2)
            level = len(numbering.split('.'))
            return (level, clean_text)

        # Pattern for simple numbering (e.g., 1.)
        match = re.match(r'^(\d+)\.\s*(.+)$', text)
        if match:
            clean_text = match.group(2)
            return (1, clean_text)

        # Pattern for letter numbering (e.g., A.)
        match = re.match(r'^([A-Z])\.\s*(.+)$', text)
        if match:
            clean_text = match.group(2)
            return (2, clean_text)

        # Pattern for Roman numerals
        match = re.match(r'^([IVX]+)\.\s*(.+)$', text)
        if match:
            clean_text = match.group(2)
            return (1, clean_text)

        return (None, text)

    def calculate_text_complexity(self, text: str) -> float:
        """
        Calculate a complexity score for text.

        This method calculates a score based on average word length and words per sentence.

        Args:
            text: Text to analyze.

        Returns:
            Complexity score (higher = more complex).
        """
        if not text:
            return 0.0

        words = text.split()
        if not words:
            return 0.0

        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Estimate sentence count
        sentences = len(re.split(r'[.!?]+', text))

        # Calculate words per sentence
        words_per_sentence = len(words) / max(sentences, 1)

        # Calculate complexity score
        complexity = (avg_word_length * 0.5) + (words_per_sentence * 0.3)

        return complexity

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        This method splits text into sentences based on punctuation marks.

        Args:
            text: Input text to split.

        Returns:
            List of sentences.
        """
        if not text:
            return []

        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)

        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                cleaned_sentences.append(sentence)

        return cleaned_sentences

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract keywords from text.

        This method identifies and returns the most frequent keywords in the text.

        Args:
            text: Input text to analyze.
            top_k: Number of top keywords to return.

        Returns:
            List of keywords.
        """
        if not text:
            return []

        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Remove stop words
        words = [word for word in words if word not in self.stop_words]

        # Count word frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top k
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, freq in sorted_words[:top_k]]
