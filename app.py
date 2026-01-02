import streamlit as st
import re
from collections import Counter
import string
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Text Analyzer",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .sentiment-positive {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sentiment-negative {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sentiment-neutral {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Sentiment word dictionaries
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 
    'brilliant', 'outstanding', 'superb', 'love', 'happy', 'joy', 'beautiful',
    'perfect', 'best', 'better', 'nice', 'positive', 'success', 'successful',
    'achievement', 'win', 'winner', 'victory', 'delighted', 'pleased', 'satisfied'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate', 'angry',
    'sad', 'disappointed', 'failure', 'fail', 'lose', 'loser', 'negative',
    'wrong', 'problem', 'issue', 'error', 'mistake', 'difficult', 'hard',
    'impossible', 'never', 'nothing', 'nobody', 'disaster', 'crisis'
}

# Analysis Functions
def analyze_text(text):
    """Comprehensive text analysis"""
    # Basic metrics
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Character count
    char_count = len(text)
    char_no_spaces = len(text.replace(' ', ''))
    
    # Word count
    word_count = len(words)
    
    # Sentence count
    sentence_count = len(sentences)
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
    
    # Average sentence length
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    # Paragraph count
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    return {
        'char_count': char_count,
        'char_no_spaces': char_no_spaces,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'avg_word_length': round(avg_word_length, 2),
        'avg_sentence_length': round(avg_sentence_length, 2)
    }

def sentiment_analysis(text):
    """Analyze sentiment of text"""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        sentiment = "Neutral"
        score = 50
    else:
        score = (positive_count / total_sentiment_words) * 100
        if score > 60:
            sentiment = "Positive"
        elif score < 40:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
    
    return {
        'sentiment': sentiment,
        'score': round(score, 1),
        'positive_words': positive_count,
        'negative_words': negative_count
    }

def keyword_extraction(text, top_n=10):
    """Extract most common keywords"""
    # Remove punctuation and convert to lowercase
    text_clean = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text_clean.split()
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their'
    }
    
    # Filter out stop words and short words
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Count frequencies
    word_freq = Counter(filtered_words)
    
    return word_freq.most_common(top_n)

def readability_score(text):
    """Calculate readability metrics"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not words or not sentences:
        return {'score': 0, 'level': 'Unknown'}
    
    # Count syllables (simplified)
    def count_syllables(word):
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        if syllable_count == 0:
            syllable_count = 1
            
        return syllable_count
    
    total_syllables = sum(count_syllables(word) for word in words)
    
    # Flesch Reading Ease Score (simplified)
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = total_syllables / len(words)
    
    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    score = max(0, min(100, score))  # Clamp between 0-100
    
    # Determine reading level
    if score >= 90:
        level = "Very Easy (5th grade)"
    elif score >= 80:
        level = "Easy (6th grade)"
    elif score >= 70:
        level = "Fairly Easy (7th grade)"
    elif score >= 60:
        level = "Standard (8th-9th grade)"
    elif score >= 50:
        level = "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        level = "Difficult (College)"
    else:
        level = "Very Difficult (College Graduate)"
    
    return {'score': round(score, 1), 'level': level}

# Header
st.markdown('<p class="main-header">🤖 AI Text Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">Analyze text with AI-powered insights on sentiment, readability, and more</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Analysis Options")
    
    analysis_type = st.multiselect(
        "Select Analysis Types",
        ["Basic Metrics", "Sentiment Analysis", "Keyword Extraction", "Readability Score"],
        default=["Basic Metrics", "Sentiment Analysis"]
    )
    
    if "Keyword Extraction" in analysis_type:
        keyword_count = st.slider("Number of Keywords", 5, 20, 10)
    else:
        keyword_count = 10
    
    st.divider()
    
    st.markdown("### 📊 Analysis History")
    if st.session_state.analysis_history:
        st.info(f"Total analyses: {len(st.session_state.analysis_history)}")
        if st.button("Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.info("No analyses yet")
    
    st.divider()
    st.markdown("### 💡 Tips")
    st.info("""
    - Paste any text to analyze
    - Works with articles, emails, essays
    - Get instant AI insights
    - Download results as JSON
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📝 Text Analysis", "📈 Advanced Metrics", "📜 History"])

with tab1:
    st.markdown("### Enter Your Text")
    
    # Sample texts
    sample_option = st.selectbox(
        "Or try a sample text:",
        ["None", "Positive Review", "Negative Review", "Technical Article", "Creative Story"]
    )
    
    sample_texts = {
        "Positive Review": "This product is absolutely amazing! I love everything about it. The quality is excellent and the customer service was outstanding. Highly recommended!",
        "Negative Review": "Terrible experience. The product is poor quality and broke after one day. Customer service was awful and unhelpful. Very disappointed.",
        "Technical Article": "Machine learning algorithms have revolutionized data analysis. Neural networks process information through interconnected nodes, enabling pattern recognition and predictive modeling.",
        "Creative Story": "The sun dipped below the horizon, painting the sky in shades of orange and purple. Sarah walked along the beach, her footprints disappearing in the waves."
    }
    
    default_text = sample_texts.get(sample_option, "")
    
    text_input = st.text_area(
        "Text to analyze",
        value=default_text,
        height=200,
        placeholder="Enter or paste your text here..."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_button = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if analyze_button and text_input:
        with st.spinner("Analyzing text..."):
            # Perform analyses
            results = {}
            
            if "Basic Metrics" in analysis_type:
                results['basic'] = analyze_text(text_input)
            
            if "Sentiment Analysis" in analysis_type:
                results['sentiment'] = sentiment_analysis(text_input)
            
            if "Keyword Extraction" in analysis_type:
                results['keywords'] = keyword_extraction(text_input, keyword_count)
            
            if "Readability Score" in analysis_type:
                results['readability'] = readability_score(text_input)
            
            # Save to history
            st.session_state.analysis_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'text_preview': text_input[:100] + "..." if len(text_input) > 100 else text_input,
                'results': results
            })
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            # Basic Metrics
            if "Basic Metrics" in analysis_type:
                st.markdown("### 📊 Basic Metrics")
                metrics = results['basic']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-value">{metrics['word_count']}</div>
                        <div class="metric-label">Words</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-value">{metrics['sentence_count']}</div>
                        <div class="metric-label">Sentences</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-value">{metrics['paragraph_count']}</div>
                        <div class="metric-label">Paragraphs</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-value">{metrics['char_count']}</div>
                        <div class="metric-label">Characters</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                col5, col6 = st.columns(2)
                with col5:
                    st.metric("Avg Word Length", f"{metrics['avg_word_length']} chars")
                with col6:
                    st.metric("Avg Sentence Length", f"{metrics['avg_sentence_length']} words")
            
            # Sentiment Analysis
            if "Sentiment Analysis" in analysis_type:
                st.markdown("### 😊 Sentiment Analysis")
                sentiment_data = results['sentiment']
                
                sentiment_class = f"sentiment-{sentiment_data['sentiment'].lower()}"
                st.markdown(f"""
                <div class="{sentiment_class}">
                    <h2 style="margin: 0;">{sentiment_data['sentiment']}</h2>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem;">Score: {sentiment_data['score']}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Positive Words", sentiment_data['positive_words'], 
                             delta="Good" if sentiment_data['positive_words'] > 0 else None)
                with col2:
                    st.metric("Negative Words", sentiment_data['negative_words'],
                             delta="Concerning" if sentiment_data['negative_words'] > 0 else None,
                             delta_color="inverse")
            
            # Keywords
            if "Keyword Extraction" in analysis_type:
                st.markdown("### 🔑 Top Keywords")
                keywords = results['keywords']
                
                # Display as columns
                cols = st.columns(3)
                for idx, (word, count) in enumerate(keywords):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.info(f"**{word}** - {count} times")
            
            # Readability
            if "Readability Score" in analysis_type:
                st.markdown("### 📖 Readability Analysis")
                readability = results['readability']
                
                score = readability['score']
                if score >= 70:
                    color = "#38ef7d"
                elif score >= 50:
                    color = "#4facfe"
                else:
                    color = "#ff6a00"
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                            padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
                    <h2 style="margin: 0;">Reading Level: {readability['level']}</h2>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem;">Readability Score: {readability['score']}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("💡 Higher scores indicate easier readability. 60-70 is considered standard for most audiences.")
            
            # Download results
            st.divider()
            report_json = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download Analysis Report (JSON)",
                data=report_json,
                file_name=f"text_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

with tab2:
    st.markdown("### 📈 Advanced Text Metrics")
    
    if text_input:
        st.markdown("#### Character Distribution")
        
        # Count different character types
        letters = sum(c.isalpha() for c in text_input)
        digits = sum(c.isdigit() for c in text_input)
        spaces = sum(c.isspace() for c in text_input)
        special = sum(not c.isalnum() and not c.isspace() for c in text_input)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Letters", letters)
        col2.metric("Digits", digits)
        col3.metric("Spaces", spaces)
        col4.metric("Special Chars", special)
        
        # Word length distribution
        st.markdown("#### Word Length Distribution")
        words = text_input.split()
        word_lengths = [len(word.strip(string.punctuation)) for word in words]
        length_dist = Counter(word_lengths)
        
        chart_data = {
            'Length': list(range(1, max(word_lengths) + 1)) if word_lengths else [0],
            'Count': [length_dist.get(i, 0) for i in range(1, max(word_lengths) + 1)] if word_lengths else [0]
        }
        
        st.bar_chart(chart_data, x='Length', y='Count')
        
    else:
        st.info("👈 Enter text in the 'Text Analysis' tab to see advanced metrics")

with tab3:
    st.markdown("### 📜 Analysis History")
    
    if st.session_state.analysis_history:
        for idx, analysis in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"Analysis {len(st.session_state.analysis_history) - idx} - {analysis['timestamp']}"):
                st.markdown(f"**Text Preview:** {analysis['text_preview']}")
                st.json(analysis['results'])
    else:
        st.info("No analysis history yet. Analyze some text to see it here!")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Built with ❤️ using Streamlit</p>
        <p style='font-size: 0.8rem;'>AI-powered text analysis tool</p>
    </div>
""", unsafe_allow_html=True
