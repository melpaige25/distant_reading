# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The `distant_reading` repository implements a computational literary analysis tool that performs "distant reading" - quantitative analysis of literary texts using natural language processing, sentiment analysis, and statistical methods. The project analyzes five 19th-century novels and provides an interactive web interface for exploring the results.

## Build and Run Commands

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Running Analysis
```bash
# Analyze all text files (pg*.txt) and generate analysis_results.json
python3 analyze_texts.py
```

This command:
- Strips Project Gutenberg headers/footers
- Tokenizes and preprocesses texts
- Creates bag-of-words with stopwords removed
- Performs sentiment analysis using VADER
- Calculates style metrics (sentence length, lexical diversity, etc.)
- Computes TF-IDF for distinctive words
- Outputs results to `analysis_results.json`

### Viewing Results
```bash
# Open the web interface in a browser
# Simply open index.html in any modern web browser
# Or use a simple HTTP server:
python3 -m http.server 8000
# Then navigate to http://localhost:8000
```

## Project Structure

```
distant_reading/
├── analyze_texts.py      # Main analysis script
├── analysis_results.json # Generated analysis data (20KB)
├── requirements.txt      # Python dependencies
├── index.html           # Web interface structure
├── styles.css           # Responsive styling
├── app.js              # Interactive visualization logic
├── pg*.txt             # Source texts (5 novels, ~2MB total)
└── CLAUDE.md           # This file
```

## Architecture

### Backend (Python)
**File**: `analyze_texts.py`

The analysis pipeline consists of:

1. **TextAnalyzer Class** - Core analysis engine
   - `strip_gutenberg_headers()` - Removes PG boilerplate
   - `preprocess_text()` - Cleans and normalizes text
   - `tokenize_words()` - Extracts alphabetic tokens
   - `create_bag_of_words()` - Builds frequency distribution
   - `analyze_sentiment()` - VADER sentiment scoring per sentence
   - `calculate_style_metrics()` - Computes linguistic statistics
   - `calculate_tfidf()` - Identifies distinctive vocabulary

2. **Output Format** - JSON array of text objects:
```json
{
  "filename": "pg2527.txt",
  "title": "The Sorrows of Young Werther",
  "author": "Johann Wolfgang von Goethe",
  "word_frequencies": {"word": count, ...},
  "sentiment": {
    "overall": {...},
    "average": {"positive": 0.x, "negative": 0.x, ...}
  },
  "style": {
    "avg_sentence_length": float,
    "lexical_diversity": float,
    ...
  },
  "distinctive_words": [{"word": str, "score": float}, ...]
}
```

### Frontend (HTML/CSS/JavaScript)
**Files**: `index.html`, `styles.css`, `app.js`

**Key Features:**
- **Single Text View**: Word cloud, sentiment bars, style metrics, distinctive words
- **Comparison Mode**: Side-by-side analysis of multiple texts with radar charts
- **Interactive Visualizations**:
  - Word clouds (wordcloud2.js)
  - Sentiment bar charts (Chart.js)
  - Style comparison radar charts

**State Management**: Vanilla JavaScript with global state object tracking current text and selected texts for comparison.

## Key Dependencies

### Python
- **nltk**: Text tokenization and stopwords (punkt, stopwords corpora)
- **vaderSentiment**: Sentiment analysis optimized for literary text
- **scikit-learn**: TF-IDF vectorization for distinctive word extraction
- **numpy**: Statistical calculations

### JavaScript (CDN)
- **Chart.js 4.4.0**: Bar and radar chart visualizations
- **wordcloud2 1.2.2**: Interactive word cloud rendering

## Texts Analyzed

1. **The Sorrows of Young Werther** by Goethe (42K words)
2. **Sentimental Education Vol. 1** by Flaubert (85K words)
3. **The Sagamore of Saco** by Smith (46K words)
4. **Adrian Savage** by Malet (139K words - largest)
5. **The Red Wizard** by Ellis (33K words)

## Performance Notes

- Analysis runtime: ~10-15 minutes for all 5 texts
- Bottleneck: Per-sentence sentiment analysis on large novels
- The script processes texts sequentially
- Web interface loads instantly once JSON is generated

## Development Workflow

1. Add new texts as `pg*.txt` files in the root directory
2. Run `python3 analyze_texts.py` to regenerate analysis
3. Refresh browser to see updated visualizations
4. The web interface automatically adapts to any number of texts

## Common Tasks

**Add a new text:**
```bash
# Add pg####.txt file to root directory
python3 analyze_texts.py  # Regenerate analysis
```

**Modify analysis parameters:**
- Edit `TextAnalyzer` class methods in `analyze_texts.py`
- Adjust stopwords, tokenization, or metrics calculation
- Re-run analysis to update JSON

**Customize visualizations:**
- Modify `app.js` for chart configurations
- Update `styles.css` for appearance changes
- No backend changes needed for frontend updates
