#!/usr/bin/env python3
"""
Distant Reading Analysis Tool
Analyzes multiple literary texts for word frequency, sentiment, and stylistic patterns.
"""

import json
import re
from pathlib import Path
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


class TextAnalyzer:
    """Analyzes literary texts for distant reading."""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def strip_gutenberg_headers(self, text):
        """Remove Project Gutenberg headers and footers."""
        # Find the start marker
        start_match = re.search(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)
        # Find the end marker
        end_match = re.search(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)

        if start_match and end_match:
            return text[start_match.end():end_match.start()].strip()
        elif start_match:
            return text[start_match.end():].strip()
        elif end_match:
            return text[:end_match.start()].strip()
        else:
            return text.strip()

    def preprocess_text(self, text):
        """Clean and preprocess text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def tokenize_words(self, text):
        """Tokenize text into words, removing punctuation."""
        # Tokenize
        words = word_tokenize(text.lower())
        # Keep only alphabetic words
        words = [word for word in words if word.isalpha()]
        return words

    def create_bag_of_words(self, words):
        """Create bag of words, removing stopwords."""
        filtered_words = [word for word in words if word not in self.stop_words]
        return Counter(filtered_words)

    def analyze_sentiment(self, text):
        """Analyze sentiment using VADER."""
        # Analyze full text
        full_sentiment = self.sentiment_analyzer.polarity_scores(text)

        # Analyze by sentences for more granular view
        sentences = sent_tokenize(text)
        sentence_sentiments = [self.sentiment_analyzer.polarity_scores(sent) for sent in sentences]

        # Calculate averages
        avg_sentiment = {
            'positive': np.mean([s['pos'] for s in sentence_sentiments]),
            'negative': np.mean([s['neg'] for s in sentence_sentiments]),
            'neutral': np.mean([s['neu'] for s in sentence_sentiments]),
            'compound': np.mean([s['compound'] for s in sentence_sentiments])
        }

        return {
            'overall': full_sentiment,
            'average': avg_sentiment,
            'sentence_count': len(sentences)
        }

    def calculate_style_metrics(self, text, words):
        """Calculate various style metrics."""
        sentences = sent_tokenize(text)

        # Sentence statistics
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        avg_sentence_length = np.mean(sentence_lengths) if sentence_lengths else 0

        # Word statistics
        word_lengths = [len(word) for word in words]
        avg_word_length = np.mean(word_lengths) if word_lengths else 0

        # Vocabulary richness (Type-Token Ratio)
        unique_words = len(set(words))
        total_words = len(words)
        ttr = unique_words / total_words if total_words > 0 else 0

        # Lexical diversity (variation of TTR for longer texts)
        # Use first 10000 words for standardization
        sample_words = words[:10000] if len(words) > 10000 else words
        lexical_diversity = len(set(sample_words)) / len(sample_words) if sample_words else 0

        return {
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'sentence_count': len(sentences),
            'word_count': total_words,
            'unique_words': unique_words,
            'type_token_ratio': round(ttr, 4),
            'lexical_diversity': round(lexical_diversity, 4)
        }

    def extract_metadata(self, text, filename):
        """Extract title and author from Project Gutenberg text."""
        lines = text.split('\n')[:100]  # Check first 100 lines

        title = None
        author = None

        for line in lines:
            if line.startswith('Title:'):
                title = line.replace('Title:', '').strip()
            elif line.startswith('Author:'):
                author = line.replace('Author:', '').strip()

        # Fallback to filename if not found
        if not title:
            title = filename.replace('.txt', '').replace('pg', 'Text ')
        if not author:
            author = "Unknown"

        return title, author

    def analyze_file(self, filepath):
        """Analyze a single text file."""
        print(f"Analyzing {filepath.name}...")

        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        # Extract metadata
        title, author = self.extract_metadata(raw_text, filepath.name)

        # Strip headers and preprocess
        clean_text = self.strip_gutenberg_headers(raw_text)
        clean_text = self.preprocess_text(clean_text)

        # Tokenize
        words = self.tokenize_words(clean_text)

        # Create bag of words
        bow = self.create_bag_of_words(words)

        # Get top words for word cloud
        top_words = dict(bow.most_common(100))

        # Analyze sentiment
        sentiment = self.analyze_sentiment(clean_text)

        # Calculate style metrics
        style = self.calculate_style_metrics(clean_text, words)

        return {
            'filename': filepath.name,
            'title': title,
            'author': author,
            'word_frequencies': top_words,
            'sentiment': sentiment,
            'style': style
        }

    def calculate_tfidf(self, texts_data):
        """Calculate TF-IDF scores for distinctive words across texts."""
        # Prepare documents
        documents = []
        for data in texts_data:
            # Reconstruct text from word frequencies
            words = []
            for word, count in data['word_frequencies'].items():
                words.extend([word] * min(count, 100))  # Cap for performance
            documents.append(' '.join(words))

        if len(documents) < 2:
            return {}

        # Calculate TF-IDF
        vectorizer = TfidfVectorizer(max_features=50)
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()

        # Get top TF-IDF words for each document
        distinctive_words = {}
        for idx, data in enumerate(texts_data):
            tfidf_scores = tfidf_matrix[idx].toarray()[0]
            top_indices = tfidf_scores.argsort()[-20:][::-1]
            distinctive_words[data['filename']] = [
                {'word': feature_names[i], 'score': round(float(tfidf_scores[i]), 4)}
                for i in top_indices if tfidf_scores[i] > 0
            ]

        return distinctive_words

    def analyze_all(self, text_directory='.'):
        """Analyze all text files in directory."""
        directory = Path(text_directory)
        text_files = sorted(directory.glob('pg*.txt'))

        if not text_files:
            print("No Project Gutenberg text files found!")
            return None

        print(f"Found {len(text_files)} text files to analyze.\n")

        # Analyze each text
        results = []
        for filepath in text_files:
            try:
                analysis = self.analyze_file(filepath)
                results.append(analysis)
            except Exception as e:
                print(f"Error analyzing {filepath.name}: {e}")

        # Calculate TF-IDF for distinctive words
        print("\nCalculating distinctive words...")
        distinctive_words = self.calculate_tfidf(results)

        # Add distinctive words to results
        for result in results:
            result['distinctive_words'] = distinctive_words.get(result['filename'], [])

        return results


def main():
    """Main execution function."""
    print("=" * 60)
    print("Distant Reading Analysis Tool")
    print("=" * 60)
    print()

    # Initialize analyzer
    analyzer = TextAnalyzer()

    # Analyze all texts
    results = analyzer.analyze_all()

    if results:
        # Save to JSON
        output_file = 'analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 60}")
        print(f"Analysis complete! Results saved to {output_file}")
        print(f"Analyzed {len(results)} texts:")
        for result in results:
            print(f"  - {result['title']} by {result['author']}")
        print(f"{'=' * 60}")
    else:
        print("No results to save.")


if __name__ == '__main__':
    main()
