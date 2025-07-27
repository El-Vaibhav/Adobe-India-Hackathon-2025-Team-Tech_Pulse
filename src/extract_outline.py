"""
Adobe India Hackathon 2025 - Challenge 1A
Outline Extractor - Intelligent heading and title detection from PDFs

This module is designed to intelligently detect and extract headings and titles from PDF documents.
It employs a combination of font analysis and pattern matching to identify document structure.
"""

import re
from typing import Dict, List, Any, Optional

# Assuming these utility classes are defined elsewhere
from src.utility import FontAnalyzer, TextProcessor

class OutlineExtractor:
    """Extracts structured outlines from PDF content using multiple strategies."""

    def __init__(self):
        """Initialize the outline extractor with necessary tools and patterns."""
        self.font_analyzer = FontAnalyzer()
        self.text_processor = TextProcessor()

        # Define heading detection patterns for various heading styles
        self.heading_patterns = {
        'english': [
            r'^\d+\.\s+(.+)$',       # Matches numbered headings like "1. Introduction"
            r'^\d+\.\d+\s+(.+)$',    # Matches sub-numbered headings like "1.1 Overview"
            r'^\d+\.\d+\.\d+\s+(.+)$', # Matches deeper sub-numbered headings like "1.1.1 Details"
            r'^[A-Z][A-Z\s]+$',      # Matches headings in ALL CAPS
            r'^[IVX]+\.\s+(.+)$',    # Matches headings with Roman numerals like "IV. Section"
            r'^[A-Z]\.\s+(.+)$',     # Matches headings like "A. Section"
            r'^\([a-z]\)\s+(.+)$',   # Matches headings like "(a) subsection"
            r'^•\s+(.+)$',           # Matches bullet point headings
            r'^-\s+(.+)$',           # Matches dash headings
        ],
        # Multilingual feature in code
        'multilingual': [
        r'^[\u4e00-\u9fff]+',    # Chinese/Japanese
        r'^[\u3040-\u309f]+',    # Hiragana
        r'^[\u30a0-\u30ff]+',    # Katakana
        r'^[\u0590-\u05ff]+',    # Hebrew
        r'^[\u0600-\u06ff]+',    # Arabic
        r'^[\u0900-\u097F]+',    # Devanagari (Hindi, Marathi, Sanskrit, etc.)
        r'^[\u0980-\u09FF]+',    # Bengali (Bangla, Assamese)
        r'^[\u0A00-\u0A7F]+',    # Gurmukhi (Punjabi)
        r'^[\u0A80-\u0AFF]+',    # Gujarati
        r'^[\u0B00-\u0B7F]+',    # Oriya (Odia)
        r'^[\u0B80-\u0BFF]+',    # Tamil
        r'^[\u0C00-\u0C7F]+',    # Telugu
        r'^[\u0C80-\u0CFF]+',    # Kannada
        r'^[\u0D00-\u0D7F]+',    # Malayalam
        r'^[\u0E00-\u0E7F]+',    # Thai
        r'^[\u0E80-\u0EFF]+',    # Lao
        r'^[\u1100-\u11FF]+',    # Hangul Jamo (Korean)
        r'^[\uAC00-\uD7AF]+',    # Hangul Syllables (Korean)
        r'^[\u0400-\u04FF]+',    # Cyrillic (Russian, Ukrainian, etc.)
        r'^[\u0370-\u03FF]+',    # Greek
    ]
      }

    def extract_title(self, metadata: Dict, pages_content: List[Dict]) -> str:
        """
        Extract document title using multiple strategies.

        This method attempts to extract the title from metadata first, then from the first page,
        and finally falls back to a default title if necessary.

        Args:
            metadata: PDF metadata dictionary which may contain the title.
            pages_content: List of page content dictionaries to analyze for potential titles.

        Returns:
            Extracted title string.
        """
        # Strategy 1: Use PDF metadata title if available and valid
        if metadata and metadata.get('title'):
            title = metadata['title'].strip()
            if title and len(title) > 3:
                print(f"Title extracted from metadata: {title}")
                return title

        # Strategy 2: Extract from first page using font analysis
        if pages_content:
            first_page = pages_content[0]
            title = self._extract_title_from_page(first_page)
            if title:
                print(f"Title extracted from first page: {title}")
                return title

        # Strategy 3: Use a generic fallback title if no title is found
        print("Using filename as title fallback")
        return "Document Title"

    def _extract_title_from_page(self, page_content: Dict) -> Optional[str]:
        """
        Extract title from the first page using font analysis.

        This method analyzes text blocks on the first page to identify potential titles
        based on font size, style, and other characteristics.

        Args:
            page_content: Dictionary containing the content of a single page.

        Returns:
            Optional string containing the extracted title, or None if no title is found.
        """
        text_dict = page_content.get('text_dict', {})

        if not text_dict or 'blocks' not in text_dict:
            return None

        candidates = []

        # Analyze text blocks for potential titles
        for block in text_dict['blocks']:
            if 'lines' not in block:
                continue

            for line in block['lines']:
                if 'spans' not in line:
                    continue

                for span in line['spans']:
                    text = span.get('text', '').strip()
                    font_size = span.get('size', 0)
                    font_flags = span.get('flags', 0)

                    # Skip empty or very short text
                    if not text or len(text) < 5:
                        continue

                    # Skip common non-title patterns
                    if any(pattern in text.lower() for pattern in ['page', 'abstract', 'introduction', 'contents', 'index']):
                        continue

                    # Calculate title score based on font characteristics
                    score = self._calculate_title_score(text, font_size, font_flags)

                    if score > 0:
                        candidates.append((text, score, font_size))

        # Return the highest scoring candidate as the title
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None

    def _calculate_title_score(self, text: str, font_size: float, font_flags: int) -> float:
        """
        Calculate a likelihood score for text being a title.

        This method assigns a score based on various characteristics such as font size,
        boldness, word count, and capitalization patterns.

        Args:
            text: The text to evaluate.
            font_size: The font size of the text.
            font_flags: The font flags indicating style attributes like bold or italic.

        Returns:
            A float score indicating the likelihood of the text being a title.
        """
        score = 0.0

        # Font size contribution (larger fonts are more likely to be titles)
        if font_size > 16:
            score += 3.0
        elif font_size > 12:
            score += 2.0
        elif font_size > 10:
            score += 1.0

        # Bold text is more likely to be a title
        if font_flags & 2**4:  # Bold flag
            score += 2.0

        # Length considerations
        word_count = len(text.split())
        if 3 <= word_count <= 10:  # Reasonable title length
            score += 1.0
        elif word_count > 15:  # Too long for a title
            score -= 1.0

        # Capitalization patterns
        if text.isupper():
            score += 1.0
        elif text.istitle():
            score += 0.5

        # Penalty for very common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        text_words = set(text.lower().split())
        if len(text_words.intersection(common_words)) > len(text_words) * 0.5:
            score -= 0.5

        return score

    def extract_headings(self, pages_content: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract hierarchical headings from all pages.

        This method processes each page to extract potential headings and then
        post-processes them to assign proper hierarchy levels.

        Args:
            pages_content: List of page content dictionaries.

        Returns:
            List of heading dictionaries with level, text, and page number.
        """
        headings = []

        for page_content in pages_content:
            page_num = page_content['page_num']
            page_headings = self._extract_headings_from_page(page_content)

            # Add page number to each heading
            for heading in page_headings:
                heading['page'] = page_num
                headings.append(heading)

        # Post-process headings to assign proper hierarchy levels
        processed_headings = self._process_heading_hierarchy(headings)

        print(f"Extracted {len(processed_headings)} headings")
        return processed_headings

    def _extract_headings_from_page(self, page_content: Dict) -> List[Dict[str, Any]]:
        """
        Extract potential headings from a single page.

        This method uses both font analysis and pattern matching to identify headings.

        Args:
            page_content: Dictionary containing the content of a single page.

        Returns:
            List of heading dictionaries with text and confidence scores.
        """
        text_dict = page_content.get('text_dict', {})
        plain_text = page_content.get('plain_text', '')

        candidates = []

        # Strategy 1: Font-based detection
        font_candidates = self._extract_by_font_analysis(text_dict)
        candidates.extend(font_candidates)

        # Strategy 2: Pattern-based detection
        pattern_candidates = self._extract_by_patterns(plain_text)
        candidates.extend(pattern_candidates)

        # Remove duplicates and sort by confidence
        unique_candidates = self._deduplicate_candidates(candidates)

        return unique_candidates

    def _extract_by_font_analysis(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """
        Extract headings based on font characteristics.

        This method identifies potential headings by analyzing font sizes and styles.

        Args:
            text_dict: Dictionary containing text blocks and their properties.

        Returns:
            List of heading dictionaries with text, confidence scores, and other attributes.
        """
        candidates = []

        if not text_dict or 'blocks' not in text_dict:
            return candidates

        # Collect all font sizes to determine relative sizes
        font_sizes = []
        for block in text_dict['blocks']:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                if 'spans' not in line:
                    continue
                for span in line['spans']:
                    size = span.get('size', 0)
                    if size > 0:
                        font_sizes.append(size)

        if not font_sizes:
            return candidates

        # Calculate font size thresholds
        avg_size = sum(font_sizes) / len(font_sizes)
        max_size = max(font_sizes)

        # Extract text with larger fonts as potential headings
        for block in text_dict['blocks']:
            if 'lines' not in block:
                continue

            for line in block['lines']:
                if 'spans' not in line:
                    continue

                # Combine text from all spans in the line
                line_text = ''
                line_size = 0
                line_flags = 0

                for span in line['spans']:
                    line_text += span.get('text', '')
                    line_size = max(line_size, span.get('size', 0))
                    line_flags |= span.get('flags', 0)

                line_text = line_text.strip()

                # Skip empty lines or very short text
                if not line_text or len(line_text) < 3:
                    continue

                # Check if this could be a heading based on font size
                size_ratio = line_size / avg_size if avg_size > 0 else 1

                if size_ratio >= 1.2 or line_size >= avg_size + 2:
                    confidence = min(size_ratio, 3.0)

                    # Boost confidence for bold text
                    if line_flags & 2**4:  # Bold
                        confidence += 0.5

                    candidates.append({
                        'text': line_text,
                        'confidence': confidence,
                        'font_size': line_size,
                        'method': 'font_analysis'
                    })

        return candidates

    def _extract_by_patterns(self, plain_text: str) -> List[Dict[str, Any]]:
        """
        Extract headings based on text patterns.

        This method identifies potential headings by matching text against predefined patterns.

        Args:
            plain_text: Plain text content of a page.

        Returns:
            List of heading dictionaries with text, confidence scores, and other attributes.
        """
        candidates = []

        lines = plain_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Test against heading patterns
            for lang, patterns in self.heading_patterns.items():
              for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Extract the heading text (removing numbering)
                    if match.groups():
                        heading_text = match.group(1).strip()
                    else:
                        heading_text = line.strip()

                    if heading_text and len(heading_text) >= 3:
                        confidence = 1.0

                        # Boost confidence for numbered patterns
                        if any(char.isdigit() for char in line[:10]):
                            confidence += 0.5

                        candidates.append({
                            'text': heading_text,
                            'confidence': confidence,
                            'pattern': pattern,
                            'method': 'pattern_matching'
                        })
                    break

        return candidates

    def _deduplicate_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate candidates and sort by confidence.

        This method ensures that only unique headings are retained and sorted by confidence.

        Args:
            candidates: List of heading dictionaries.

        Returns:
            List of unique heading dictionaries sorted by confidence.
        """
        seen_texts = set()
        unique_candidates = []

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        for candidate in candidates:
            text = candidate['text'].lower().strip()

            # Skip if we've seen similar text
            if text in seen_texts:
                continue

            # Skip very short headings
            if len(text) < 3:
                continue

            # Skip headings that are too long (likely not headings)
            if len(text) > 200:
                continue

            seen_texts.add(text)
            unique_candidates.append(candidate)

        return unique_candidates

    def _process_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process headings to assign proper hierarchy levels (H1, H2, H3).

        This method assigns hierarchy levels to headings based on font sizes and patterns.

        Args:
            headings: List of heading dictionaries.

        Returns:
            List of heading dictionaries with assigned hierarchy levels.
        """
        if not headings:
            return []

        # Sort headings by confidence and font size
        sorted_headings = sorted(headings, key=lambda x: (
            x.get('confidence', 0),
            x.get('font_size', 0)
        ), reverse=True)

        # Assign hierarchy levels based on font sizes and patterns
        processed = []
        font_size_to_level = {}

        for heading in sorted_headings:
            text = heading['text']
            font_size = heading.get('font_size', 12)
            page = heading['page']

            # Determine hierarchy level
            level = self._determine_heading_level(text, font_size, font_size_to_level)

            processed.append({
                'level': level,
                'text': text,
                'page': page
            })

        # Sort by page number to maintain document order
        processed.sort(key=lambda x: x['page'])

        return processed

    def _determine_heading_level(self, text: str, font_size: float, font_size_to_level: Dict[float, str]) -> str:
        """
        Determine the hierarchy level (H1, H2, H3) for a heading.

        This method assigns a hierarchy level based on text patterns and font sizes.

        Args:
            text: The heading text.
            font_size: The font size of the heading.
            font_size_to_level: Dictionary mapping font sizes to hierarchy levels.

        Returns:
            A string representing the hierarchy level (H1, H2, H3).
        """
        # Check for explicit numbering patterns
        if re.match(r'^\d+\.\s+', text):
            return 'H1'
        elif re.match(r'^\d+\.\d+\s+', text):
            return 'H2'
        elif re.match(r'^\d+\.\d+\.\d+\s+', text):
            return 'H3'

        # Use font size mapping
        if font_size in font_size_to_level:
            return font_size_to_level[font_size]

        # Assign level based on relative font size
        existing_sizes = sorted(font_size_to_level.keys(), reverse=True)

        if not existing_sizes:
            # First heading - assign H1
            font_size_to_level[font_size] = 'H1'
            return 'H1'

        # Compare with existing font sizes
        if font_size > existing_sizes[0]:
            # Larger than existing - this is H1, demote others
            new_mapping = {font_size: 'H1'}
            for size in existing_sizes:
                current_level = font_size_to_level[size]
                if current_level == 'H1':
                    new_mapping[size] = 'H2'
                elif current_level == 'H2':
                    new_mapping[size] = 'H3'
                else:
                    new_mapping[size] = 'H3'
            font_size_to_level.update(new_mapping)
            return 'H1'

        elif font_size >= existing_sizes[0]:
            # Same as largest - also H1
            font_size_to_level[font_size] = 'H1'
            return 'H1'

        elif len(existing_sizes) == 1:
            # Second font size - assign H2
            font_size_to_level[font_size] = 'H2'
            return 'H2'

        else:
            # Third or smaller font size - assign H3
            font_size_to_level[font_size] = 'H3'
            return 'H3'
