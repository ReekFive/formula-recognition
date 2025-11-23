# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based mathematical formula recognition tool that converts formula images to LaTeX and MathML formats, specifically optimized for Microsoft Word compatibility. The system uses Pix2Text OCR engine for formula recognition and implements a custom LaTeX-to-MathML converter with Word-specific optimizations.

## Development Commands

### Setup and Running
```bash
# Setup environment (recommended)
python scripts/setup.py

# Run the application
python scripts/run.py

# Or manual setup
pip install -r requirements.txt
python app.py
```

### Testing
```bash
# Quick test
python scripts/test.py

# Specific test suites
python tests/test_complex_formula.py
python tests/test_complete_conversion.py
python tests/test_full_pipeline.py
python tests/test_cleaning.py
```

### Access
Web interface at `http://localhost:8081`

## Architecture

### Core Processing Pipeline
1. **Image Upload** → Flask receives image file
2. **Recognition** → `FormulaRecognizer` (recognizer.py) uses Pix2Text OCR
3. **Conversion** → `FormulaConverter` (converter.py) orchestrates conversion
4. **MathML Generation** → `WordMathMLConverter` (final_converter.py) creates Word-compatible output
5. **Response** → Returns LaTeX and MathML to client

### Key Components

**FormulaRecognizer (recognizer.py)**
- Handles image preprocessing: grayscale conversion, Gaussian blur, adaptive thresholding, morphological operations
- Uses Pix2Text OCR engine for formula recognition
- Cleans LaTeX output by removing erroneous `\left`/`\right` commands and formatting symbols
- Singleton instance initialized at app startup

**FormulaConverter (converter.py)**
- Primary conversion coordinator
- Uses `latex2mathml` library with `SymPy` as fallback
- Delegates to `WordMathMLConverter` for Word-compatible MathML generation
- Returns dict with `latex`, `mathml_word_compatible`, and `latex_display` fields

**WordMathMLConverter (final_converter.py)**
- Custom LaTeX parser implementing recursive descent parsing
- Generates Word-compatible MathML with proper namespace declarations
- Handles complex structures: fractions (`\frac`), subscripts/superscripts, Greek letters, parentheses
- Critical for Word compatibility - do not bypass this component

**Flask Application (app.py)**
- Three main endpoints:
  - `POST /upload` - File upload with recognition and conversion
  - `POST /api/recognize` - API for recognition from file path
  - `POST /api/convert` - API for LaTeX-to-MathML conversion only
- Singleton instances of `FormulaRecognizer` and `FormulaConverter` initialized at startup
- Max upload size: 16MB
- Allowed formats: png, jpg, jpeg, gif, bmp, tiff

### Critical Implementation Details

**LaTeX Cleaning**
The `_clean_latex_formula` method in recognizer.py removes problematic artifacts from Pix2Text output:
- Strips `$$`, `$`, `\[`, `\]`, `\(`, `\)` delimiters
- Removes `\left` and `\right` commands that cause parsing issues
- Uses regex to avoid breaking actual LaTeX commands

**MathML Structure**
Word-compatible MathML requires:
- XML declaration: `<?xml version="1.0"?>`
- Namespace: `xmlns="http://www.w3.org/1998/Math/MathML"`
- Proper nesting of `<msub>`, `<msup>`, `<msubsup>` for subscripts/superscripts
- Use `<mfrac>` for fractions, `<mi>` for identifiers, `<mn>` for numbers, `<mo>` for operators

**Parser State Management**
`final_converter.py` uses position-based parsing - returns `(result, length)` tuples where `length` indicates how many characters were consumed. This allows proper nesting and lookahead.

## Common Development Patterns

### Adding New LaTeX Commands
1. Add command handler in `WordMathMLConverter._parse_command()`
2. Implement specific parser method (e.g., `_parse_sqrt()`)
3. Add test case in `tests/test_complex_formula.py`

### Debugging Recognition Issues
1. Check preprocessed image at `{filename}_processed.{ext}`
2. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
3. Test with `scripts/test.py` for quick iteration

### Handling Conversion Failures
The system has fallback layers:
1. Primary: `latex2mathml` library
2. Fallback: SymPy conversion
3. Final: `WordMathMLConverter` for Word-specific output

## Important Constraints

- **Do not modify Pix2Text initialization** - it requires specific model downloads on first run
- **Preserve Word MathML structure** - Word is strict about MathML format; deviations break rendering
- **Image preprocessing is critical** - disabled preprocessing reduces accuracy significantly
- **Parser methods must return tuples** - `(result_list, consumed_length)` format is required for correct parsing

## File Organization

**Production code**: `app.py`, `recognizer.py`, `converter.py`, `final_converter.py`
**Test files**: `tests/` directory contains organized test suites
**Debug scripts**: Root-level `debug_*.py` and `test_*.py` files are development artifacts
**Utilities**: `scripts/` contains setup, run, and test utilities

Note: Many debug/test files in the root are development artifacts from iterative improvements to the MathML parser.
