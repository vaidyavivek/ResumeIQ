# import streamlit as st
# import PyPDF2
# import io
# import os
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# st.set_page_config(page_title="AI Resume Critiquer",
#                    page_icon="📄", layout="centered")

# st.title("AI Resume Critiquer")
# st.markdown(
#     "Upload your resume in PDF format, and the AI will provide feedback and suggestions for improvement.")
# st.text("Hello")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# uploaded_file = st.file_uploader(
#     "Upload your resume (PDF)", type=["pdf", "txt"])
# Job_role = st.text_input("Enter the job role you are applying for(Optional):")

# analyze_button = st.button("Analyze Resume")


# def extract_text_from_pdf(pdf_file):
#     pdf_reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text() + "\n"
#     return text


# def extract_text_from_file(uploaded_file):
#     if uploaded_file.type == "application/pdf":
#         # pdf_reader = PyPDF2.PdfReader(uploaded_file)
#         return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
#     return uploaded_file.read().decode("utf-8")


# if analyze_button and uploaded_file:
#     try:
#         file_content = extract_text_from_file(uploaded_file)

#         if not file_content.strip():
#             st.error("The uploaded file is empty or could not be read.")
#             st.stop()

#         prompt = f"""Please analyze the following resume and provide feedback, suggestions for improvement, and any potential issues. If a job role is provided, tailor the feedback to that role. Resume content: {file_content}
#         Focus on the following aspects:
#         1. Clarity and conciseness of the content.
#         2. Relevance of the information to the job role(if provided).
#         3. Formatting and structure of the resume.
#         4. Any missing key information that should be included.

#         Resume content: {file_content}

#         Please provide your feedback in a structured format, highlighting strengths, areas for improvement, and specific suggestions for enhancing the resume."""

#         client = OpenAI(api_key=OPENAI_API_KEY)
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert resume reviewer."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=1000
#         )
#         st.markdown("### Analysis Result")
#         st.markdown(response.choices[0].message.content)
#     except Exception as e:
#         st.error(f"An error occurred while processing the resume: {str(e)}")

import streamlit as st
import PyPDF2
import io
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background: #F8F9FB; }

.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 3rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
}
.hero h1 {
    color: white;
    font-size: 2.4rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}
.hero p { color: #94a3b8; font-size: 1.05rem; margin: 0; }
.hero .badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}

.score-ring {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}
.score-number {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
}
.score-high { color: #10b981; }
.score-mid { color: #f59e0b; }
.score-low { color: #ef4444; }

.section-score {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid #f1f5f9;
}
.section-score:last-child { border-bottom: none; }
.progress-bar {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    flex: 1;
    margin: 0 12px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.keyword-chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    margin: 2px;
}
.kw-found { background: #d1fae5; color: #065f46; }
.kw-missing { background: #fee2e2; color: #991b1b; }

.tab-content { padding: 1rem 0; }

.insight-row {
    display: flex;
    gap: 8px;
    align-items: flex-start;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f8fafc;
}
.insight-icon { font-size: 1rem; flex-shrink: 0; margin-top: 2px; }
.insight-text { font-size: 0.9rem; color: #374151; line-height: 1.5; }

.stButton > button {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    transition: background 0.2s;
    width: 100%;
}
.stButton > button:hover { background: #4338ca; }

.upload-area {
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: #f8fafc;
    margin-bottom: 1rem;
}

h3 { color: #0f172a; font-weight: 600; }
h4 { color: #1e293b; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    return uploaded_file.read().decode("utf-8")


def analyze_resume(client, resume_text, job_role, job_description):
    jd_section = f"\n\nJob Description:\n{job_description}" if job_description else ""
    role_section = f"Target Role: {job_role}" if job_role else "No specific role provided."

    prompt = f"""You are an expert ATS resume analyzer and career coach. Analyze the resume below and return a JSON object with this exact structure:

{{
  "ats_score": <integer 0-100>,
  "summary": "<2-sentence overall verdict>",
  "sections": {{
    "impact": {{ "score": <0-100>, "feedback": "<specific feedback>" }},
    "formatting": {{ "score": <0-100>, "feedback": "<specific feedback>" }},
    "keywords": {{ "score": <0-100>, "feedback": "<specific feedback>" }},
    "experience": {{ "score": <0-100>, "feedback": "<specific feedback>" }},
    "education": {{ "score": <0-100>, "feedback": "<specific feedback>" }}
  }},
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>", "<improvement 4>"],
  "keywords_found": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
  "keywords_missing": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
  "bullet_rewrites": [
    {{ "original": "<original bullet>", "improved": "<improved bullet>" }},
    {{ "original": "<original bullet>", "improved": "<improved bullet>" }}
  ],
  "interview_questions": [
    "<question 1>",
    "<question 2>",
    "<question 3>",
    "<question 4>",
    "<question 5>"
  ]
}}

{role_section}{jd_section}

Resume:
{resume_text}

Return ONLY valid JSON. No markdown, no explanation."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert ATS resume analyzer. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_cover_letter(client, resume_text, job_role, job_description):
    prompt = f"""Write a compelling, personalized cover letter based on this resume for the role of {job_role}.

Resume:
{resume_text}

Job Description:
{job_description if job_description else 'Not provided'}

Write 3 short paragraphs. Be specific, reference real experience from the resume, and avoid generic phrases. Do not use "I am writing to apply" as the opener. Make it human and direct."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert career coach who writes compelling, specific cover letters."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content


def score_color_class(score):
    if score >= 75:
        return "score-high"
    elif score >= 50:
        return "score-mid"
    return "score-low"


def progress_color(score):
    if score >= 75:
        return "#10b981"
    elif score >= 50:
        return "#f59e0b"
    return "#ef4444"


st.markdown("""
<div class="hero">
    <div class="badge">AI-POWERED</div>
    <h1>ResumeIQ</h1>
    <p>Get your ATS score, keyword analysis, bullet rewrites, and interview prep — in seconds.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.markdown("#### Upload your resume")
    uploaded_file = st.file_uploader(
        "", type=["pdf", "txt"], label_visibility="collapsed")

    st.markdown("#### Target role")
    job_role = st.text_input(
        "", placeholder="e.g. AI Engineer, Product Manager", label_visibility="collapsed")

    st.markdown("#### Job description (optional but recommended)")
    job_description = st.text_area(
        "", placeholder="Paste the job description here for tailored keyword analysis...", height=140, label_visibility="collapsed")

    analyze_clicked = st.button("Analyze Resume →", use_container_width=True)

    if uploaded_file and analyze_clicked and not job_role:
        st.warning("Add a target role for better results.")

with col2:
    if analyze_clicked and uploaded_file:
        if not OPENAI_API_KEY:
            st.error("OpenAI API key not found. Add it to your .env file.")
            st.stop()

        with st.spinner("Analyzing your resume..."):
            try:
                resume_text = extract_text_from_file(uploaded_file)
                if not resume_text.strip():
                    st.error("Could not read the file. Try a different PDF.")
                    st.stop()

                client = OpenAI(api_key=OPENAI_API_KEY)
                data = analyze_resume(
                    client, resume_text, job_role, job_description)

                score = data.get("ats_score", 0)
                color_class = score_color_class(score)

                st.markdown(f"""
                <div class="score-ring">
                    <div>
                        <div class="score-number {color_class}">{score}</div>
                        <div style="font-size:0.75rem;color:#94a3b8;margin-top:2px">ATS SCORE</div>
                    </div>
                    <div>
                        <div style="font-weight:500;color:#0f172a;margin-bottom:4px">{'Strong' if score >= 75 else 'Needs work' if score >= 50 else 'Weak'} resume</div>
                        <div style="font-size:0.88rem;color:#64748b;line-height:1.5">{data.get('summary', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                tab1, tab2, tab3, tab4 = st.tabs(
                    ["📊 Analysis", "🔑 Keywords", "✏️ Rewrites", "🎤 Interview Prep"])

                with tab1:
                    st.markdown("**Section scores**")
                    sections = data.get("sections", {})
                    section_labels = {
                        "impact": "Impact & achievements",
                        "formatting": "Formatting & structure",
                        "keywords": "Keyword optimization",
                        "experience": "Experience relevance",
                        "education": "Education & certs"
                    }
                    for key, label in section_labels.items():
                        if key in sections:
                            s = sections[key]["score"]
                            color = progress_color(s)
                            st.markdown(f"""
                            <div class="section-score">
                                <span style="font-size:0.85rem;color:#374151;min-width:160px">{label}</span>
                                <div class="progress-bar"><div class="progress-fill" style="width:{s}%;background:{color}"></div></div>
                                <span style="font-size:0.85rem;font-weight:500;color:{color};min-width:32px">{s}</span>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**✅ Strengths**")
                        for s in data.get("strengths", []):
                            st.markdown(
                                f"""<div class="insight-row"><div class="insight-icon">✓</div><div class="insight-text">{s}</div></div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown("**⚡ Improvements**")
                        for i in data.get("improvements", []):
                            st.markdown(
                                f"""<div class="insight-row"><div class="insight-icon">→</div><div class="insight-text">{i}</div></div>""", unsafe_allow_html=True)

                with tab2:
                    st.markdown("**Keywords found in your resume**")
                    found_html = "".join(
                        [f'<span class="keyword-chip kw-found">✓ {k}</span>' for k in data.get("keywords_found", [])])
                    st.markdown(
                        f'<div style="margin-bottom:1rem">{found_html}</div>', unsafe_allow_html=True)

                    st.markdown("**Keywords you should add**")
                    missing_html = "".join(
                        [f'<span class="keyword-chip kw-missing">✗ {k}</span>' for k in data.get("keywords_missing", [])])
                    st.markdown(f'<div>{missing_html}</div>',
                                unsafe_allow_html=True)

                with tab3:
                    st.markdown("**Before → After bullet rewrites**")
                    for i, rewrite in enumerate(data.get("bullet_rewrites", [])):
                        st.markdown(f"""
                        <div class="card" style="margin-bottom:0.75rem">
                            <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:4px">ORIGINAL</div>
                            <div style="font-size:0.88rem;color:#64748b;margin-bottom:10px;line-height:1.5">{rewrite.get('original', '')}</div>
                            <div style="font-size:0.8rem;color:#10b981;margin-bottom:4px">IMPROVED</div>
                            <div style="font-size:0.88rem;color:#0f172a;line-height:1.5;font-weight:500">{rewrite.get('improved', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with tab4:
                    st.markdown("**Likely interview questions for this role**")
                    for i, q in enumerate(data.get("interview_questions", []), 1):
                        st.markdown(f"""
                        <div class="insight-row" style="padding:0.75rem 0">
                            <div style="font-size:0.85rem;font-weight:600;color:#4f46e5;min-width:24px">Q{i}</div>
                            <div class="insight-text">{q}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if job_role:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Generate cover letter →"):
                            with st.spinner("Writing your cover letter..."):
                                cover = generate_cover_letter(
                                    client, resume_text, job_role, job_description)
                                st.markdown("**Your cover letter**")
                                st.markdown(
                                    f'<div class="card" style="white-space:pre-wrap;font-size:0.9rem;line-height:1.7;color:#374151">{cover}</div>', unsafe_allow_html=True)
                                st.download_button(
                                    "Download cover letter", cover, file_name="cover_letter.txt")

            except json.JSONDecodeError:
                st.error("Analysis failed — try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.markdown("""
        <div style="padding:3rem 2rem;text-align:center;color:#94a3b8">
            <div style="font-size:3rem;margin-bottom:1rem">📄</div>
            <div style="font-size:1rem;font-weight:500;color:#64748b;margin-bottom:0.5rem">Upload your resume to get started</div>
            <div style="font-size:0.85rem">You'll get an ATS score, keyword gaps, bullet rewrites, and interview prep</div>
        </div>
        """, unsafe_allow_html=True)
