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


class TextAnalyzer:
    """Analyzes literary texts for distant reading."""

    def __init__(self):
        # Base stopwords
        self.stop_words = set(stopwords.words('english'))

        # Extended stopwords for 19th-century literature
        literary_stopwords = {
            # Common narrative words
            'said', 'upon', 'would', 'could', 'one', 'two', 'three',
            'may', 'might', 'must', 'shall', 'will', 'though', 'yet',
            'thus', 'indeed', 'therefore', 'however', 'moreover',
            # Titles and honorifics
            'mr', 'mrs', 'miss', 'sir', 'lord', 'lady', 'master',
            # Common verbs that don't add meaning
            'came', 'went', 'saw', 'looked', 'seemed', 'made', 'took',
            'gave', 'found', 'knew', 'thought', 'felt', 'began',
            # Time words
            'day', 'time', 'moment', 'hour', 'night', 'morning',
            # Pronouns and basic words
            'little', 'great', 'old', 'new', 'long', 'good', 'first',
            'last', 'much', 'many', 'own', 'ever', 'never', 'still',
            'even', 'well', 'back', 'thing', 'things', 'way',
            # Chapter markers
            'chapter', 'volume', 'part', 'book', 'section'
        }
        self.stop_words.update(literary_stopwords)

        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Romantic vocabulary lexicon
        self.romantic_lexicon = {
            'love': ['love', 'loved', 'loving', 'lover', 'lovers', 'beloved', 'adore', 'adored', 'adoring', 'adoration'],
            'yearning': ['yearning', 'yearn', 'yearned', 'longing', 'long', 'longed', 'desire', 'desired', 'desiring',
                        'wish', 'wished', 'wishing', 'hope', 'hoped', 'hoping', 'pine', 'pined', 'pining'],
            'affection': ['affection', 'affectionate', 'tender', 'tenderness', 'fond', 'fondness', 'devotion',
                         'devoted', 'attachment', 'attached', 'passion', 'passionate'],
            'pain': ['pain', 'painful', 'anguish', 'anguished', 'sorrow', 'sorrowful', 'grief', 'grieved',
                    'melancholy', 'despair', 'despairing', 'heartbreak', 'heartbroken', 'torment', 'tormented',
                    'suffering', 'suffer', 'suffered', 'misery', 'miserable', 'wretched', 'agony'],
            'loss': ['loss', 'lost', 'forsaken', 'abandoned', 'rejection', 'rejected', 'unrequited',
                    'separated', 'separation', 'parted', 'parting', 'farewell']
        }

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

    def analyze_romantic_vocabulary(self, words):
        """Analyze romantic vocabulary usage in the text."""
        # Flatten all romantic words into a single list
        all_romantic_words = []
        for category_words in self.romantic_lexicon.values():
            all_romantic_words.extend(category_words)

        # Count occurrences
        word_counts = Counter(words)
        romantic_usage = {}

        for category, word_list in self.romantic_lexicon.items():
            category_counts = {}
            for word in word_list:
                count = word_counts.get(word, 0)
                if count > 0:
                    category_counts[word] = count

            romantic_usage[category] = {
                'words': category_counts,
                'total': sum(category_counts.values()),
                'unique': len(category_counts)
            }

        # Calculate overall romantic vocabulary density
        total_romantic = sum(cat['total'] for cat in romantic_usage.values())
        total_words = len(words)
        density = (total_romantic / total_words * 100) if total_words > 0 else 0

        return {
            'categories': romantic_usage,
            'total_romantic_words': total_romantic,
            'density_percentage': round(density, 3)
        }

    def analyze_emotional_arc(self, text):
        """Analyze how sentiment changes throughout the text (beginning, middle, end)."""
        sentences = sent_tokenize(text)
        total_sentences = len(sentences)

        if total_sentences < 3:
            return None

        # Divide into 3 segments - faster analysis
        segment_size = total_sentences // 3
        segments = []

        for i in range(3):
            start_idx = i * segment_size
            if i == 2:  # Last segment gets any remaining sentences
                end_idx = total_sentences
            else:
                end_idx = (i + 1) * segment_size

            segment_sentences = sentences[start_idx:end_idx]

            # Analyze sentiment for this segment
            segment_sentiments = [self.sentiment_analyzer.polarity_scores(sent) for sent in segment_sentences]

            avg_sentiment = {
                'positive': np.mean([s['pos'] for s in segment_sentiments]),
                'negative': np.mean([s['neg'] for s in segment_sentiments]),
                'neutral': np.mean([s['neu'] for s in segment_sentiments]),
                'compound': np.mean([s['compound'] for s in segment_sentiments])
            }

            segments.append({
                'segment': i + 1,
                'label': ['Beginning', 'Middle', 'End'][i],
                'sentiment': avg_sentiment,
                'sentence_count': len(segment_sentences)
            })

        return {
            'segments': segments,
            'total_segments': 3
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

        # Analyze romantic vocabulary
        romantic_vocab = self.analyze_romantic_vocabulary(words)

        # Analyze emotional arc
        emotional_arc = self.analyze_emotional_arc(clean_text)

        return {
            'filename': filepath.name,
            'title': title,
            'author': author,
            'word_frequencies': top_words,
            'sentiment': sentiment,
            'style': style,
            'romantic_vocabulary': romantic_vocab,
            'emotional_arc': emotional_arc
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
