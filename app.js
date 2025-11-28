// Global state
let analysisData = [];
let currentText = null;
let selectedTexts = new Set();

// Load and initialize
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('analysis_results.json');
        analysisData = await response.json();
        initializeApp();
    } catch (error) {
        console.error('Error loading analysis data:', error);
        document.getElementById('text-details').innerHTML = `
            <div class="welcome-message">
                <h2>Error Loading Data</h2>
                <p>Could not load analysis_results.json. Please run the Python analysis script first.</p>
                <p style="color: #dc3545; margin-top: 20px;">Command: <code>python3 analyze_texts.py</code></p>
            </div>
        `;
    }
});

function initializeApp() {
    renderTextList();
    renderComparisonCheckboxes();
    setupEventListeners();
}

function renderTextList() {
    const textList = document.getElementById('text-list');
    textList.innerHTML = analysisData.map((text, index) => `
        <div class="text-item" data-index="${index}">
            <h3>${text.title}</h3>
            <p>by ${text.author}</p>
        </div>
    `).join('');
}

function renderComparisonCheckboxes() {
    const container = document.getElementById('comparison-checkboxes');
    container.innerHTML = analysisData.map((text, index) => `
        <div class="comparison-checkbox">
            <input type="checkbox" id="compare-${index}" value="${index}">
            <label for="compare-${index}">${text.title}</label>
        </div>
    `).join('');
}

function setupEventListeners() {
    // Text selection
    document.querySelectorAll('.text-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            selectText(index);
        });
    });

    // Comparison checkboxes
    document.querySelectorAll('.comparison-checkbox input').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const index = parseInt(e.target.value);
            if (e.target.checked) {
                selectedTexts.add(index);
            } else {
                selectedTexts.delete(index);
            }
            updateCompareButton();
        });
    });

    // Compare button
    document.getElementById('compare-btn').addEventListener('click', () => {
        showComparison();
    });
}

function selectText(index) {
    currentText = analysisData[index];

    // Update active state
    document.querySelectorAll('.text-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-index="${index}"]`).classList.add('active');

    // Show single view
    document.getElementById('single-view').classList.remove('hidden');
    document.getElementById('comparison-view').classList.add('hidden');

    renderTextDetails(currentText);
}

function renderTextDetails(text) {
    const container = document.getElementById('text-details');

    container.innerHTML = `
        <div class="text-header">
            <h2>${text.title}</h2>
            <p class="author">by ${text.author}</p>
            <p class="metadata">
                ${text.style.word_count.toLocaleString()} words |
                ${text.style.sentence_count.toLocaleString()} sentences
            </p>
        </div>

        <div class="analysis-section">
            <h3>📊 Word Cloud</h3>
            <div class="wordcloud-container">
                <canvas id="wordcloud"></canvas>
            </div>
        </div>

        <div class="analysis-section">
            <h3>💭 Sentiment Analysis</h3>
            <div class="sentiment-display">
                <div class="sentiment-bar">
                    <div class="label">Positive</div>
                    <div class="bar-container">
                        <div class="bar-fill positive" style="width: ${text.sentiment.average.positive * 100}%"></div>
                    </div>
                    <div class="value">${(text.sentiment.average.positive * 100).toFixed(1)}%</div>
                </div>
                <div class="sentiment-bar">
                    <div class="label">Negative</div>
                    <div class="bar-container">
                        <div class="bar-fill negative" style="width: ${text.sentiment.average.negative * 100}%"></div>
                    </div>
                    <div class="value">${(text.sentiment.average.negative * 100).toFixed(1)}%</div>
                </div>
                <div class="sentiment-bar">
                    <div class="label">Neutral</div>
                    <div class="bar-container">
                        <div class="bar-fill neutral" style="width: ${text.sentiment.average.neutral * 100}%"></div>
                    </div>
                    <div class="value">${(text.sentiment.average.neutral * 100).toFixed(1)}%</div>
                </div>
                <div class="sentiment-bar">
                    <div class="label">Compound</div>
                    <div class="bar-container">
                        <div class="bar-fill compound" style="width: ${((text.sentiment.average.compound + 1) / 2) * 100}%"></div>
                    </div>
                    <div class="value">${text.sentiment.average.compound.toFixed(3)}</div>
                </div>
            </div>
        </div>

        <div class="analysis-section">
            <h3>📏 Style Metrics</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="label">Avg Sentence Length</div>
                    <div class="value">${text.style.avg_sentence_length}</div>
                    <div class="label">words</div>
                </div>
                <div class="metric-card">
                    <div class="label">Avg Word Length</div>
                    <div class="value">${text.style.avg_word_length}</div>
                    <div class="label">characters</div>
                </div>
                <div class="metric-card">
                    <div class="label">Unique Words</div>
                    <div class="value">${text.style.unique_words.toLocaleString()}</div>
                    <div class="label">distinct</div>
                </div>
                <div class="metric-card">
                    <div class="label">Lexical Diversity</div>
                    <div class="value">${text.style.lexical_diversity}</div>
                    <div class="label">ratio</div>
                </div>
            </div>
        </div>

        ${text.distinctive_words && text.distinctive_words.length > 0 ? `
        <div class="analysis-section">
            <h3>✨ Distinctive Words</h3>
            <div class="distinctive-words">
                ${text.distinctive_words.slice(0, 15).map(item =>
                    `<span class="word-badge">${item.word}</span>`
                ).join('')}
            </div>
        </div>
        ` : ''}
    `;

    // Render word cloud
    renderWordCloud(text.word_frequencies);
}

function renderWordCloud(wordFreqs) {
    const canvas = document.getElementById('wordcloud');
    if (!canvas) return;

    // Prepare data for wordcloud2
    const wordList = Object.entries(wordFreqs).map(([word, freq]) => [word, freq]);

    // Clear previous cloud
    canvas.width = canvas.offsetWidth;
    canvas.height = 400;

    // Generate word cloud
    WordCloud(canvas, {
        list: wordList,
        gridSize: 8,
        weightFactor: function(size) {
            return Math.pow(size, 0.5) * 3;
        },
        fontFamily: 'Segoe UI, sans-serif',
        color: function() {
            const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'];
            return colors[Math.floor(Math.random() * colors.length)];
        },
        rotateRatio: 0.3,
        backgroundColor: '#f8f9fa'
    });
}

function updateCompareButton() {
    const button = document.getElementById('compare-btn');
    button.disabled = selectedTexts.size < 2;
    button.textContent = selectedTexts.size === 0
        ? 'Compare Selected'
        : `Compare ${selectedTexts.size} Texts`;
}

function showComparison() {
    if (selectedTexts.size < 2) return;

    // Hide single view, show comparison
    document.getElementById('single-view').classList.add('hidden');
    document.getElementById('comparison-view').classList.remove('hidden');

    const textsToCompare = Array.from(selectedTexts).map(index => analysisData[index]);
    renderComparison(textsToCompare);
}

function renderComparison(texts) {
    const container = document.getElementById('comparison-view');

    container.innerHTML = `
        <div class="comparison-header">
            <h2>Comparing ${texts.length} Texts</h2>
            <p>Side-by-side analysis of selected literary works</p>
        </div>

        <div class="analysis-section">
            <h3>📊 Word Clouds Comparison</h3>
            <div class="comparison-grid">
                ${texts.map((text, index) => `
                    <div class="comparison-text">
                        <h3>${text.title}</h3>
                        <p style="color: #6c757d; margin-bottom: 15px;">${text.author}</p>
                        <canvas id="compare-cloud-${index}" class="comparison-wordcloud"></canvas>
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="analysis-section">
            <h3>💭 Sentiment Comparison</h3>
            <div class="chart-container">
                <canvas id="sentiment-chart"></canvas>
            </div>
        </div>

        <div class="analysis-section">
            <h3>📏 Style Metrics Comparison</h3>
            <div class="chart-container">
                <canvas id="style-chart"></canvas>
            </div>
        </div>

        <div class="analysis-section">
            <h3>📖 Detailed Metrics</h3>
            <div class="comparison-grid">
                ${texts.map(text => `
                    <div class="comparison-text">
                        <h3>${text.title}</h3>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="label">Words</div>
                                <div class="value">${text.style.word_count.toLocaleString()}</div>
                            </div>
                            <div class="metric-card">
                                <div class="label">Sentences</div>
                                <div class="value">${text.style.sentence_count.toLocaleString()}</div>
                            </div>
                            <div class="metric-card">
                                <div class="label">Avg Sentence</div>
                                <div class="value">${text.style.avg_sentence_length}</div>
                            </div>
                            <div class="metric-card">
                                <div class="label">Lexical Diversity</div>
                                <div class="value">${text.style.lexical_diversity}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    // Render word clouds for each text
    texts.forEach((text, index) => {
        const canvas = document.getElementById(`compare-cloud-${index}`);
        if (canvas) {
            canvas.width = canvas.offsetWidth;
            canvas.height = 300;
            const wordList = Object.entries(text.word_frequencies).map(([word, freq]) => [word, freq]);
            WordCloud(canvas, {
                list: wordList,
                gridSize: 6,
                weightFactor: function(size) {
                    return Math.pow(size, 0.5) * 2;
                },
                fontFamily: 'Segoe UI, sans-serif',
                color: function() {
                    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'];
                    return colors[Math.floor(Math.random() * colors.length)];
                },
                rotateRatio: 0.3,
                backgroundColor: 'white'
            });
        }
    });

    // Render sentiment chart
    renderSentimentChart(texts);

    // Render style chart
    renderStyleChart(texts);
}

function renderSentimentChart(texts) {
    const ctx = document.getElementById('sentiment-chart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: texts.map(t => t.title),
            datasets: [
                {
                    label: 'Positive',
                    data: texts.map(t => (t.sentiment.average.positive * 100).toFixed(1)),
                    backgroundColor: 'rgba(40, 167, 69, 0.7)',
                    borderColor: 'rgb(40, 167, 69)',
                    borderWidth: 1
                },
                {
                    label: 'Negative',
                    data: texts.map(t => (t.sentiment.average.negative * 100).toFixed(1)),
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: 'rgb(220, 53, 69)',
                    borderWidth: 1
                },
                {
                    label: 'Neutral',
                    data: texts.map(t => (t.sentiment.average.neutral * 100).toFixed(1)),
                    backgroundColor: 'rgba(108, 117, 125, 0.7)',
                    borderColor: 'rgb(108, 117, 125)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Score Comparison'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

function renderStyleChart(texts) {
    const ctx = document.getElementById('style-chart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Avg Sentence Length',
                'Avg Word Length',
                'Lexical Diversity',
                'Vocabulary Richness'
            ],
            datasets: texts.map((text, index) => {
                const colors = [
                    'rgba(102, 126, 234, 0.6)',
                    'rgba(118, 75, 162, 0.6)',
                    'rgba(240, 147, 251, 0.6)',
                    'rgba(79, 172, 254, 0.6)',
                    'rgba(67, 233, 123, 0.6)'
                ];
                return {
                    label: text.title,
                    data: [
                        text.style.avg_sentence_length / 30 * 100, // Normalize to ~100
                        text.style.avg_word_length / 6 * 100,
                        text.style.lexical_diversity * 100,
                        text.style.type_token_ratio * 100
                    ],
                    backgroundColor: colors[index % colors.length],
                    borderColor: colors[index % colors.length].replace('0.6', '1'),
                    borderWidth: 2
                };
            })
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Style Metrics Comparison (Normalized)'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}
