# Adobe India Hackathon 2025 – Challenge 1A

## 📄 PDF Structured Outline Extraction – Heading Detection Pipeline

###🚀 Overview
This solution is designed to process PDF files and extract structured outlines by detecting headings (H1, H2, H3). It handles a variety of PDF layouts using font analysis, text pattern detection, and efficient resource utilization. The result is saved in a validated JSON format adhering to the challenge's schema.

###🧩 Approach Summary

##PDF Parsing

We use PyMuPDF to read and analyze the structure of PDF documents, extracting text, font sizes, font styles (bold/italic), and metadata.

# # Heading Detection Logic

Headings are identified based on a combination of:

Font Size Hierarchy – Larger fonts are mapped to H1, H2, H3 levels.

Boldness (Font Flags) – Bold text likely indicates headings.

Content Patterns – Regex rules detect numbering (1., 1.1., A., etc.), Title Case, and ALL CAPS.

Contextual Heuristics – Headings are usually short, not stop-word-heavy, and avoid sentence punctuation.

# # Schema Validation

The extracted title and heading outline are validated using jsonschema against the Challenge 1A official schema.

Warnings or errors are reported if schema violations are detected.

# # Performance Optimization

Optimized processing ensures low memory usage and fast execution using efficient loops and font caching.

Resource monitoring tracks CPU time and memory, validating compliance with hackathon constraints.

### Output Format

```json
{
"title": "Understanding AI",
"outline": [
 { "level": "H1", "text": "Introduction", "page": 1 },
 { "level": "H2", "text": "What is AI?", "page": 2 },
 { "level": "H3", "text": "History of AI", "page": 3 }
]
}

```
# # # 📦 Project Structure and Code Roles
| **File**                 | **Purpose**                                                                                  |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| `main.py`                | Main entry point – orchestrates the entire pipeline, monitors performance, and saves output. |
| `src/process_pdf.py`         | Core processor – extracts text from PDF, calls the outline extractor, and saves JSON.        |
| `src/extract_outline.py` | Heading detection – analyzes fonts and text content to detect heading structure.             |
| `src/utility.py`             | Utility classes – font analysis and text processing (e.g., keyword extraction, regex).       |
| `src/validate_schema.py`     | Validates JSON output using official schema; reports warnings and tips.                      |


# # # 📚 Models and Libraries Used
| **Library**      | **Purpose**                                           |
| ---------------- | ----------------------------------------------------- |
| `PyMuPDF (fitz)` | PDF text extraction with font/style metadata          |
| `re`             | Regex pattern matching for heading detection          |
| `jsonschema`     | Schema validation of output JSON                      |
| `time`, `psutil` | Performance monitoring: elapsed time and memory usage |


No external ML models are used; the solution is rule-based for reliability and speed.

## Docker Configuration

### Base Image

- `python:3.10-slim` for minimal footprint
- AMD64 platform compatibility
- Offline operation (no network access)

### Container Specifications

- **Input**: Read-only mount at `/app/input`
- **Output**: Write mount at `/app/output`
- **Network**: Disabled (`--network none`)
- **Memory**: Optimized for 16GB constraint
- **CPU**: Utilizes 8 available cores

## Usage

### Building the Image

```bash
docker build --platform linux/amd64 -t none team_tech_pulse_solution_1:69 .
```

### Running the Container

```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none team_tech_pulse_solution_1:69
```

### Input/Output

- **Input**: Place PDF files in `input/` directory
- **Output**: JSON files generated in `output/` directory
- **Naming**: `document.pdf` → `document.json`

## Testing Strategy

### Test Cases

1. **Simple PDFs**: Basic documents with clear heading hierarchy
2. **Complex PDFs**: Multi-column layouts, tables, images
3. **Large PDFs**: 50+ page documents for performance testing
4. **Multilingual PDFs**: Documents in various languages
5. **Academic Papers**: Research papers with typical academic structure

### Validation

- Output JSON schema validation
- Performance benchmarking
- Memory usage monitoring
- Cross-platform compatibility testing

## Performance Metrics

### Target Performance

- **Processing Time**: ≤ 10 seconds for 50-page PDF
- **Memory Usage**: ≤ 16GB RAM
- **Model Size**: ≤ 200MB total
- **CPU Efficiency**: Optimal use of 8 cores


