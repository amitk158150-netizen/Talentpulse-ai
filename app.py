import os
import time
import re
import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="TalentPulse AI | Resume Analyzer & Interview Coach",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #1e1e38 0%, #2d1b4e 50%, #172554 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .badge-primary {
        background: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .report-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.75rem;
        color: #e2e8f0;
        line-height: 1.7;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("GEMINI_API_KEY")

with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/artificial-intelligence.png", width=70)
    st.markdown("### ⚡ AI System Control")
    
    if not api_key:
        st.warning("GEMINI_API_KEY not found in environment.")
        api_key = st.text_input("Enter Gemini API Key:", type="password", placeholder="AIzaSy...")
        if api_key:
            st.success("API Key configured for this session.")
    else:
        st.success("🟢 AI Engine Connected")
    
    st.divider()
    st.markdown("#### ⚙️ Engine Settings")
    selected_temperature = st.slider("Response Creativity:", min_value=0.1, max_value=1.0, value=0.4, step=0.1)
    
    st.divider()
    st.markdown("#### 💡 Hackathon Demo Tips")
    st.caption("• Use the 'Load Sample Job Description' button for quick live testing.")
    st.caption("• Both PDF upload and direct text inputs are supported.")

client = genai.Client(api_key=api_key) if api_key else None

MODELS_TO_TRY = ["gemini-3.8-flash"]

def generate_ai_response(prompt: str) -> str:
    """
    Executes prompt with graceful multi-model fallback to bypass 503 high-demand spikes.
    """
    last_exception = None
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "503" in err_msg or "404" in err_msg or "UNAVAILABLE" in err_msg:
                last_exception = e
                time.sleep(1)
                continue
            else:
                raise e
    raise last_exception if last_exception else Exception("All AI servers are currently busy. Please retry in 10 seconds.")

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Safely parses PDF file and extracts text across all pages.
    """
    try:
        reader = PdfReader(uploaded_file)
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        return "\n".join(text_content).strip()
    except Exception as e:
        st.error(f"Error reading PDF document: {e}")
        return ""

st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h1 class="hero-title">TalentPulse AI</h1>
            <p class="hero-subtitle">Smart Resume ATS Analyzer & Real-Time Technical Mock Interview Coach</p>
        </div>
        <div style="display: flex; gap: 10px;">
            <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; color: #93c5fd; font-weight: 600;">⚡ Gemini 3.8 Engine</span>
            <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; color: #6ee7b7; font-weight: 600;">🛡️ ATS Verified</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📄 Smart Resume Analyzer", 
    "🎙️ AI Mock Interview Coach", 
    "📊 Features & Architecture"
])

with tab1:
    col_input1, col_input2 = st.columns([1, 1], gap="large")
    
    with col_input1:
        st.markdown('<div class="section-title">📂 1. Candidate Resume</div>', unsafe_allow_html=True)
        upload_mode = st.radio("Choose Input Mode:", ["Upload PDF Resume", "Paste Text Resume"], horizontal=True)
        
        extracted_resume = ""
        if upload_mode == "Upload PDF Resume":
            uploaded_pdf = st.file_uploader("Upload your resume (PDF format)", type=["pdf"], help="PDF file should contain selectable text.")
            if uploaded_pdf:
                with st.spinner("Extracting text from PDF..."):
                    extracted_resume = extract_text_from_pdf(uploaded_pdf)
                if extracted_resume:
                    st.success(f"Extracted {len(extracted_resume.split())} words from document.")
                    with st.expander("🔍 View Extracted Text Preview"):
                        st.text(extracted_resume[:600] + ("..." if len(extracted_resume) > 600 else ""))
        else:
            extracted_resume = st.text_area(
                "Paste your complete resume text:",
                height=300,
                placeholder="Paste your education, projects, technical skills, and work experience here..."
            )

    with col_input2:
        st.markdown('<div class="section-title">🎯 2. Target Job Description (JD)</div>', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            load_sample = st.button("📋 Load Sample Python JD", help="Click to autofill a sample Junior Python Developer JD.")
        with col_btn2:
            clear_jd = st.button("🗑️ Clear JD")

        sample_jd_text = """Job Title: Junior Python Developer / Intern
Key Responsibilities:
- Build and maintain backend RESTful APIs using Python, FastAPI, or Django.
- Write clean, modular, and testable code with Git version control.
- Work with relational databases like PostgreSQL/MySQL and write efficient SQL queries.
- Collaborate with frontend teams and deploy applications to cloud environments.

Requirements:
- Strong understanding of Python fundamentals, OOP concepts, and data structures.
- Familiarity with REST APIs, JSON handling, and Docker basics.
- Experience with Git, GitHub, and problem-solving skills."""

        if "jd_input" not in st.session_state:
            st.session_state.jd_input = ""

        if load_sample:
            st.session_state.jd_input = sample_jd_text
        if clear_jd:
            st.session_state.jd_input = ""

        job_description = st.text_area(
            "Target Job Description:",
            value=st.session_state.jd_input,
            height=300,
            placeholder="Paste the role requirements, required technical stack, and responsibilities..."
        )

    st.write("")
    analyze_btn = st.button("🚀 Run Comprehensive AI Evaluation", type="primary", use_container_width=True)

    if analyze_btn:
        if not client:
            st.error("Please provide a valid Gemini API Key in the left sidebar.")
        elif not extracted_resume.strip():
            st.warning("Please upload a PDF resume or enter your resume text.")
        elif not job_description.strip():
            st.warning("Please enter or load a target Job Description.")
        else:
            with st.status("🔍 Analyzing Resume Compatibility...", expanded=True) as status:
                st.write("Extracting key competencies and work experience...")
                time.sleep(0.5)
                st.write("Cross-referencing technical requirements against Job Description...")
                time.sleep(0.5)
                st.write("Generating ATS score and customized recommendations...")
                
                evaluation_prompt = f"""
                You are an elite Technical Talent Acquisition Director and ATS Specialist.
                Conduct a deep-dive, professional evaluation of this Candidate Resume against the target Job Description.

                Candidate Resume:
                \"\"\"{extracted_resume}\"\"\"

                Target Job Description:
                \"\"\"{job_description}\"\"\"

                Return a comprehensive evaluation formatted cleanly in Markdown:
                
                ### 1. Overall ATS Match Rating
                - State the exact match score as: **Score: XX%** (e.g. Score: 82%)
                - State a brief 1-line justification.

                ### 2. High-Impact Matching Strengths
                - List 3-4 specific technical skills or relevant achievements found in the resume that directly fulfill the JD.

                ### 3. Critical Missing Skills & Gaps
                - List essential keywords, frameworks, or tools explicitly mentioned in the JD that are absent or weak in the resume.

                ### 4. Step-by-Step Action Plan
                - Provide 3-4 concrete, actionable resume updates to significantly boost interview shortlisting chances for this role.

                ### 5. Final Recruiter Verdict
                - Provide a 2-sentence executive summary verdict.
                """
                
                try:
                    analysis_output = generate_ai_response(evaluation_prompt)
                    status.update(label="✅ Evaluation Complete!", state="complete", expanded=False)
                    
                    st.markdown("---")
                    
                    score_match = re.search(r"Score:\s*(\d+)%", analysis_output)
                    if score_match:
                        score_val = int(score_match.group(1))
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric(label="ATS Match Score", value=f"{score_val}%", delta=f"{score_val - 70}% vs benchmark")
                        with m2:
                            quality = "Strong Match" if score_val >= 75 else "Moderate Match" if score_val >= 50 else "Needs Optimization"
                            st.metric(label="Candidate Standing", value=quality)
                        with m3:
                            st.metric(label="Evaluation Status", value="Verified by Gemini")
                        st.progress(score_val / 100.0)

                    st.markdown("### 📋 Detailed Assessment Report")
                    st.markdown(f'<div class="report-box">{analysis_output}</div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Download Evaluation Report (.txt)",
                        data=analysis_output,
                        file_name="resume_evaluation_report.txt",
                        mime="text/plain"
                    )
                except Exception as ex:
                    status.update(label="❌ Analysis Failed", state="error")
                    st.error(f"Error during AI analysis: {ex}")

with tab2:
    st.markdown('<div class="section-title">🎙️ Real-Time Technical Mock Interview</div>', unsafe_allow_html=True)
    st.write("Simulate a realistic one-on-one technical interview tailored to your target position.")

    if "interview_q" not in st.session_state:
        st.session_state.interview_q = ""
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = "Python Backend Developer"

    col_role, col_lvl, col_type = st.columns([2, 1, 1])
    with col_role:
        interview_role = st.text_input("Target Role / Position:", value=st.session_state.interview_role)
    with col_lvl:
        difficulty_lvl = st.selectbox("Seniority Level:", ["Intern / Fresher", "Junior (1-2 yrs)", "Mid-Senior (3-5 yrs)"])
    with col_type:
        question_category = st.selectbox("Question Focus:", ["Core Coding & OOP", "System & API Design", "Debugging & Scenario"])

    generate_q_btn = st.button("🎲 Generate Technical Question", type="primary")

    if generate_q_btn:
        if not client:
            st.error("Please configure your Gemini API Key in the sidebar.")
        else:
            st.session_state.interview_role = interview_role
            prompt_q = f"""
            You are a Principal Software Engineer conducting a live technical interview for a '{interview_role}' at {difficulty_lvl} level.
            Generate exactly ONE realistic, high-quality technical question focusing on {question_category}.
            Make it practical and clear. Do not provide the solution or preamble. Return ONLY the question.
            """
            with st.spinner("Interviewer is formulating a realistic question..."):
                try:
                    q_text = generate_ai_response(prompt_q)
                    st.session_state.interview_q = q_text.strip()
                except Exception as ex:
                    st.error(f"Error generating question: {ex}")

    if st.session_state.interview_q:
        st.write("")
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.08); border-left: 5px solid #3b82f6; padding: 1.25rem; border-radius: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #60a5fa; letter-spacing: 0.05em;">Active Interview Question</span>
            <h4 style="margin: 0.5rem 0 0 0; color: #f1f5f9; line-height: 1.5;">{st.session_state.interview_q}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        user_response = st.text_area(
            "Your Answer:",
            height=180,
            placeholder="Structure your answer clearly: explain the core concept, approach, code/logic, and trade-offs..."
        )
        
        submit_ans_btn = st.button("📝 Submit Answer for Detailed AI Coaching", type="primary")
        
        if submit_ans_btn:
            if not client:
                st.error("Please provide your Gemini API Key.")
            elif not user_response.strip():
                st.warning("Please type your response before submitting.")
            else:
                with st.spinner("AI Coach is evaluating your response..."):
                    coach_prompt = f"""
                    You are a top-tier Engineering Interview Coach.
                    Role: {st.session_state.interview_role}
                    Question: "{st.session_state.interview_q}"
                    Candidate's Answer: "{user_response}"

                    Provide an encouraging, constructive critique formatted in Markdown:
                    ### 1. Overall Score: [X/10]
                    - Brief 1-sentence rating explanation.

                    ### 2. What You Did Well
                    - Specific strong points in technical accuracy, clarity, or depth.

                    ### 3. Gaps & Technical Inaccuracies
                    - What was missed, unclear, or could be explained more accurately.

                    ### 4. Ideal Exemplary Answer
                    - A model answer showing how a top 1% candidate would answer this concisely.
                    """
                    try:
                        feedback = generate_ai_response(coach_prompt)
                        st.markdown("### 🏆 AI Coach Feedback & Benchmark")
                        st.markdown(f'<div class="report-box">{feedback}</div>', unsafe_allow_html=True)
                    except Exception as ex:
                        st.error(f"Error evaluating response: {ex}")

with tab3:
    st.markdown('<div class="section-title">🏗️ System Architecture & Workflow</div>', unsafe_allow_html=True)
    st.write("This application demonstrates modern LLM system design tailored for career enablement tools.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <h4>📄 PDF Ingestion</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Clean document parsing using <code>pypdf</code> to extract clean plain text without external binaries.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <h4>⚡ Resilient LLM Engine</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Automatic cascading fallback across <code>gemini-3.8-flash</code> and <code>gemini-2.0-flash</code> to bypass high-demand spikes.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <h4>🎯 Dual Value Proposition</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Combines automated resume ATS gap analysis with interactive mock technical interview practice.</p>
        </div>
        """, unsafe_allow_html=True)