import streamlit as st
import anthropic
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📄 AI Resume Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Get instant AI-powered feedback on your resume</p>', unsafe_allow_html=True)

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    job_role = st.text_input("Target Job Role (Optional)", placeholder="e.g., Software Engineer")
    industry = st.selectbox(
        "Industry",
        ["Technology", "Finance", "Healthcare", "Marketing", "Education", "Other"]
    )
    experience_level = st.selectbox(
        "Experience Level",
        ["Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior Level (6-10 years)", "Executive (10+ years)"]
    )
    
    st.divider()
    st.markdown("### 💡 Tips")
    st.info("""
    - Upload in PDF or TXT format
    - Include all relevant sections
    - Be specific about achievements
    - Use action verbs
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "📊 Analysis Results", "💼 Job Match"])

with tab1:
    st.markdown("### Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'pdf'],
        help="Upload your resume in TXT or PDF format"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        with col2:
            st.info(f"📏 Size: {uploaded_file.size / 1024:.2f} KB")
        
        # Read file content
        if uploaded_file.type == "text/plain":
            resume_text = uploaded_file.read().decode('utf-8')
        else:
            st.warning("PDF parsing requires PyPDF2. For this demo, please upload a TXT file.")
            resume_text = None
        
        # Display resume preview
        if resume_text:
            with st.expander("👁️ Preview Resume Content"):
                st.text_area("Resume Text", resume_text, height=300, disabled=True)
            
            # Analyze button
            if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your resume..."):
                    try:
                        # Call Claude API
                        client = anthropic.Anthropic()
                        
                        analysis_prompt = f"""Analyze this resume and provide detailed feedback in JSON format.

Resume:
{resume_text}

Target Role: {job_role if job_role else "General"}
Industry: {industry}
Experience Level: {experience_level}

Provide analysis in this exact JSON structure:
{{
    "overall_score": <number 0-100>,
    "strengths": [<list of 3-5 key strengths>],
    "weaknesses": [<list of 3-5 areas for improvement>],
    "keyword_analysis": {{
        "present": [<list of good keywords found>],
        "missing": [<list of important keywords missing>]
    }},
    "sections_feedback": {{
        "summary": "<feedback on summary/objective>",
        "experience": "<feedback on work experience>",
        "education": "<feedback on education>",
        "skills": "<feedback on skills section>"
    }},
    "formatting_score": <number 0-100>,
    "ats_compatibility": <number 0-100>,
    "recommendations": [<list of 5-7 specific actionable recommendations>]
}}

Provide only the JSON object, no other text."""

                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=2000,
                            messages=[
                                {"role": "user", "content": analysis_prompt}
                            ]
                        )
                        
                        # Parse response
                        response_text = message.content[0].text
                        # Clean up response if needed
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0].strip()
                        
                        analysis = json.loads(response_text)
                        
                        st.session_state.analysis_result = analysis
                        st.session_state.analysis_done = True
                        st.success("✅ Analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.info("💡 Note: This app requires an Anthropic API key to be set in your environment.")

with tab2:
    if st.session_state.analysis_done and st.session_state.analysis_result:
        analysis = st.session_state.analysis_result
        
        # Overall Score
        st.markdown("### 🎯 Overall Resume Score")
        score = analysis.get('overall_score', 0)
        st.markdown(f'<div class="score-box">{score}/100</div>', unsafe_allow_html=True)
        
        # Score interpretation
        if score >= 80:
            st.success("🌟 Excellent! Your resume is in great shape.")
        elif score >= 60:
            st.info("👍 Good resume, with room for improvement.")
        else:
            st.warning("⚠️ Your resume needs significant improvements.")
        
        # Two columns for strengths and weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Strengths")
            for strength in analysis.get('strengths', []):
                st.success(f"• {strength}")
        
        with col2:
            st.markdown("### ⚠️ Areas for Improvement")
            for weakness in analysis.get('weaknesses', []):
                st.warning(f"• {weakness}")
        
        # Keyword Analysis
        st.markdown("### 🔑 Keyword Analysis")
        kw_col1, kw_col2 = st.columns(2)
        
        with kw_col1:
            st.markdown("**Present Keywords:**")
            keywords = analysis.get('keyword_analysis', {}).get('present', [])
            for kw in keywords[:10]:
                st.markdown(f"✓ {kw}")
        
        with kw_col2:
            st.markdown("**Missing Keywords:**")
            missing = analysis.get('keyword_analysis', {}).get('missing', [])
            for kw in missing[:10]:
                st.markdown(f"✗ {kw}")
        
        # Section Feedback
        st.markdown("### 📋 Section-by-Section Feedback")
        sections = analysis.get('sections_feedback', {})
        for section, feedback in sections.items():
            with st.expander(f"**{section.title()}**"):
                st.write(feedback)
        
        # Scores
        st.markdown("### 📊 Detailed Scores")
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            formatting = analysis.get('formatting_score', 0)
            st.metric("Formatting Score", f"{formatting}/100")
        
        with metric_col2:
            ats = analysis.get('ats_compatibility', 0)
            st.metric("ATS Compatibility", f"{ats}/100")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        recommendations = analysis.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
        
        # Download report
        st.divider()
        report_json = json.dumps(analysis, indent=2)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=report_json,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.info("👈 Upload and analyze a resume to see results here.")

with tab3:
    st.markdown("### 💼 Job Description Matching")
    st.write("Compare your resume against a specific job description")
    
    job_description = st.text_area(
        "Paste Job Description",
        height=200,
        placeholder="Paste the job description here..."
    )
    
    if job_description and st.session_state.analysis_done:
        if st.button("🎯 Calculate Match Score", use_container_width=True):
            with st.spinner("Calculating match..."):
                st.info("🚧 Job matching feature coming soon! This would compare your resume against the specific job description.")
    elif not st.session_state.analysis_done:
        st.warning("Please analyze your resume first in the Upload tab.")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Built with ❤️ using Streamlit and Claude AI</p>
        <p style='font-size: 0.8rem;'>AI-powered resume analysis for job seekers</p>
    </div>
""", unsafe_allow_html=True)
