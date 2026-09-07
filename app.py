import streamlit as st
import os
import json
import re
from datetime import datetime

from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =====================================================
# 2. LOAD API KEY
# =====================================================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:

    st.error(
        "GOOGLE_API_KEY is missing from your .env file."
    )

    st.stop()


# =====================================================
# 3. GEMINI CLIENT
# =====================================================

client = genai.Client(
    api_key=api_key
)


# =====================================================
# 4. SKILL DATABASE
# =====================================================

SKILLS = [

    # Programming
    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "typescript",
    "sql",

    # Data
    "machine learning",
    "deep learning",
    "data analysis",
    "data science",
    "statistics",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",

    # AI
    "artificial intelligence",
    "ai",
    "nlp",
    "natural language processing",
    "llm",
    "large language model",
    "generative ai",
    "genai",
    "rag",
    "retrieval augmented generation",
    "prompt engineering",
    "embeddings",
    "vector database",
    "faiss",

    # LLM frameworks
    "langchain",
    "langgraph",
    "llamaindex",

    # Backend
    "fastapi",
    "flask",
    "django",
    "rest api",
    "api",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",
    "database",

    # Cloud / DevOps
    "aws",
    "azure",
    "google cloud",
    "docker",
    "kubernetes",
    "git",
    "github",
    "ci/cd",

    # SAP
    "sap",
    "abap",
    "sap hana",
    "sap s/4hana",
    "sap fiori"
]


# =====================================================
# 5. SESSION STATE
# =====================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

if "jd_skills" not in st.session_state:
    st.session_state.jd_skills = []

if "matching_skills" not in st.session_state:
    st.session_state.matching_skills = []

if "missing_skills" not in st.session_state:
    st.session_state.missing_skills = []

if "match_score" not in st.session_state:
    st.session_state.match_score = 0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =====================================================
# 6. SKILL EXTRACTION
# =====================================================

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = re.escape(skill)

        if re.search(
            r"\b" + pattern + r"\b",
            text
        ):

            found_skills.append(skill)

    return sorted(
        set(found_skills)
    )


# =====================================================
# 7. RESET FUNCTION
# =====================================================

def reset_analysis():

    st.session_state.analysis = None
    st.session_state.resume_text = ""
    st.session_state.job_description = ""
    st.session_state.resume_skills = []
    st.session_state.jd_skills = []
    st.session_state.matching_skills = []
    st.session_state.missing_skills = []
    st.session_state.match_score = 0
    st.session_state.chat_history = []


# =====================================================
# 8. TITLE
# =====================================================

st.title("📄 AI Resume Analyzer & Job Matcher")

st.write(
    "Analyze your resume against a job description "
    "using Python-based skill matching and Gemini AI."
)


# =====================================================
# 9. SIDEBAR
# =====================================================

with st.sidebar:

    st.header("⚙️ Controls")

    if st.button(
        "🔄 Reset Analysis"
    ):

        reset_analysis()

        st.rerun()

    st.divider()

    st.write(
        "### Features"
    )

    st.write(
        "✅ Resume analysis"
    )

    st.write(
        "✅ Skill matching"
    )

    st.write(
        "✅ AI insights"
    )

    st.write(
        "✅ Interview questions"
    )

    st.write(
        "✅ Resume chat"
    )

    st.write(
        "✅ Download reports"
    )


# =====================================================
# 10. RESUME UPLOAD
# =====================================================

st.subheader("📄 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your Resume PDF",
    type=["pdf"]
)


# =====================================================
# 11. EXTRACT RESUME
# =====================================================

resume_text = ""

if uploaded_file:

    reader = PdfReader(
        uploaded_file
    )

    for page in reader.pages:

        text = page.extract_text()

        if text:

            resume_text += text


    if not resume_text.strip():

        st.error(
            "Could not extract text from this PDF."
        )

        st.stop()


    st.success(
        "Resume uploaded successfully! ✅"
    )


    with st.expander(
        "📑 View Extracted Resume Text"
    ):

        st.text_area(
            "Resume content",
            resume_text,
            height=300
        )


# =====================================================
# 12. JOB DESCRIPTION
# =====================================================

st.subheader("💼 Job Description")

job_description = st.text_area(
    "Paste the Job Description here",
    height=250,
    placeholder="""
Example:

We are looking for an AI Engineer with experience
in Python, Machine Learning, NLP, LLMs, RAG,
LangChain, FastAPI and SQL.
"""
)


# =====================================================
# 13. ANALYZE
# =====================================================

if uploaded_file and job_description:

    st.success(
        "Resume and Job Description are ready. ✅"
    )


    if st.button(
        "🤖 Analyze Resume",
        type="primary"
    ):

        # =================================================
        # EXTRACT SKILLS
        # =================================================

        resume_skills = extract_skills(
            resume_text
        )

        jd_skills = extract_skills(
            job_description
        )


        # =================================================
        # MATCHING SKILLS
        # =================================================

        matching_skills = sorted(
            set(resume_skills)
            &
            set(jd_skills)
        )


        # =================================================
        # MISSING SKILLS
        # =================================================

        missing_skills = sorted(
            set(jd_skills)
            -
            set(resume_skills)
        )


        # =================================================
        # CALCULATE SCORE
        # =================================================

        if jd_skills:

            match_score = round(
                (
                    len(matching_skills)
                    /
                    len(jd_skills)
                )
                * 100
            )

        else:

            match_score = 0


        # =================================================
        # GEMINI PROMPT
        # =================================================

        prompt = f"""
You are an expert technical recruiter and
AI resume analyzer.

Analyze the candidate's resume against the
job description.

========================
RESUME
========================

{resume_text}

========================
JOB DESCRIPTION
========================

{job_description}

========================
PYTHON SKILL ANALYSIS
========================

Resume skills:
{resume_skills}

Job skills:
{jd_skills}

Matching skills:
{matching_skills}

Missing skills:
{missing_skills}

Python calculated match score:
{match_score}%

========================
TASK
========================

Return VALID JSON ONLY.

Use exactly this structure:

{{
    "strengths": [],
    "areas_to_improve": [],
    "resume_suggestions": [],
    "interview_questions": []
}}

Rules:

1. Do not invent candidate experience.

2. Use only the information provided.

3. Explain the candidate's relevant strengths.

4. Explain important skill gaps.

5. Give practical resume suggestions.

6. Generate exactly 5 interview questions.

7. Interview questions should be relevant
   to the job description and candidate's
   actual background.

8. Do not claim that the candidate has a
   skill that is not present in the resume.
"""


        # =================================================
        # CALL GEMINI
        # =================================================

        with st.spinner(
            "Gemini is analyzing your resume..."
        ):

            try:

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                raw_response = response.text.strip()


                # Remove markdown fences

                if raw_response.startswith(
                    "```json"
                ):

                    raw_response = raw_response[7:]


                if raw_response.startswith(
                    "```"
                ):

                    raw_response = raw_response[3:]


                if raw_response.endswith(
                    "```"
                ):

                    raw_response = raw_response[:-3]


                raw_response = raw_response.strip()


                # Convert to dictionary

                analysis = json.loads(
                    raw_response
                )


                # Save everything

                st.session_state.analysis = analysis

                st.session_state.resume_text = (
                    resume_text
                )

                st.session_state.job_description = (
                    job_description
                )

                st.session_state.resume_skills = (
                    resume_skills
                )

                st.session_state.jd_skills = (
                    jd_skills
                )

                st.session_state.matching_skills = (
                    matching_skills
                )

                st.session_state.missing_skills = (
                    missing_skills
                )

                st.session_state.match_score = (
                    match_score
                )

                st.session_state.chat_history = []


                st.success(
                    "Analysis completed successfully! ✅"
                )


            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an invalid JSON response."
                )

                st.code(
                    raw_response
                )


            except Exception as e:

                error_message = str(e)

                if "429" in error_message:

                    st.error(
                        "⚠️ Gemini quota has been reached. "
                        "Please try again after the quota resets."
                    )

                elif "503" in error_message:

                    st.error(
                        "⚠️ Gemini is temporarily busy. "
                        "Please try again later."
                    )

                else:

                    st.error(
                        "Gemini API error."
                    )

                    st.error(
                        error_message
                    )


# =====================================================
# 14. LOAD SAVED ANALYSIS
# =====================================================

if st.session_state.analysis:

    analysis = st.session_state.analysis

    resume_skills = (
        st.session_state.resume_skills
    )

    jd_skills = (
        st.session_state.jd_skills
    )

    matching_skills = (
        st.session_state.matching_skills
    )

    missing_skills = (
        st.session_state.missing_skills
    )

    match_score = (
        st.session_state.match_score
    )


    # =================================================
    # DASHBOARD
    # =================================================

    st.divider()

    st.header(
        "📊 Resume Analysis Dashboard"
    )


    # =================================================
    # SCORE
    # =================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🎯 Skill Match Score",
            f"{match_score}%"
        )

    with col2:

        st.metric(
            "✅ Matching Skills",
            len(matching_skills)
        )

    with col3:

        st.metric(
            "❌ Missing Skills",
            len(missing_skills)
        )


    # Progress bar

    st.progress(
        match_score / 100
    )


    # =================================================
    # SKILL ANALYSIS
    # =================================================

    st.divider()

    st.header(
        "🛠️ Skill Analysis"
    )

    col1, col2 = st.columns(2)


    # -------------------------------------------------
    # MATCHING
    # -------------------------------------------------

    with col1:

        st.subheader(
            "✅ Matching Skills"
        )

        if matching_skills:

            for skill in matching_skills:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.info(
                "No matching skills detected."
            )


    # -------------------------------------------------
    # MISSING
    # -------------------------------------------------

    with col2:

        st.subheader(
            "❌ Missing Skills"
        )

        if missing_skills:

            for skill in missing_skills:

                st.error(
                    f"✗ {skill}"
                )

        else:

            st.success(
                "No major missing skills detected."
            )


    # =================================================
    # DETECTED SKILLS
    # =================================================

    col1, col2 = st.columns(2)


    with col1:

        with st.expander(
            "📄 Resume Skills"
        ):

            if resume_skills:

                st.write(
                    ", ".join(resume_skills)
                )

            else:

                st.write(
                    "No recognized skills."
                )


    with col2:

        with st.expander(
            "💼 Job Required Skills"
        ):

            if jd_skills:

                st.write(
                    ", ".join(jd_skills)
                )

            else:

                st.write(
                    "No recognized skills."
                )


    # =================================================
    # AI INSIGHTS
    # =================================================

    st.divider()

    st.header(
        "🤖 AI Insights"
    )


    # =================================================
    # STRENGTHS
    # =================================================

    st.subheader(
        "💪 Candidate Strengths"
    )

    strengths = analysis.get(
        "strengths",
        []
    )

    for strength in strengths:

        st.write(
            f"• {strength}"
        )


    # =================================================
    # AREAS TO IMPROVE
    # =================================================

    st.subheader(
        "⚠️ Areas to Improve"
    )

    areas = analysis.get(
        "areas_to_improve",
        []
    )

    for area in areas:

        st.write(
            f"• {area}"
        )


    # =================================================
    # RESUME SUGGESTIONS
    # =================================================

    st.divider()

    st.header(
        "📝 Resume Improvement Suggestions"
    )

    suggestions = analysis.get(
        "resume_suggestions",
        []
    )

    for number, suggestion in enumerate(
        suggestions,
        start=1
    ):

        st.write(
            f"**{number}.** {suggestion}"
        )


    # =================================================
    # INTERVIEW QUESTIONS
    # =================================================

    st.divider()

    st.header(
        "🎤 Personalized Interview Questions"
    )

    questions = analysis.get(
        "interview_questions",
        []
    )

    for number, question in enumerate(
        questions,
        start=1
    ):

        with st.expander(
            f"Question {number}"
        ):

            st.write(
                question
            )


    # =================================================
    # DOWNLOAD REPORT
    # =================================================

    st.divider()

    st.header(
        "📥 Download Analysis"
    )


    # Create report dictionary

    report = {

        "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "match_score":
            match_score,

        "resume_skills":
            resume_skills,

        "job_required_skills":
            jd_skills,

        "matching_skills":
            matching_skills,

        "missing_skills":
            missing_skills,

        "ai_analysis":
            analysis
    }


    # JSON report

    json_report = json.dumps(
        report,
        indent=4
    )


    st.download_button(
        label="📥 Download JSON Report",
        data=json_report,
        file_name="resume_analysis.json",
        mime="application/json"
    )


    # Text report

    text_report = f"""
AI RESUME ANALYSIS REPORT
=========================

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

MATCH SCORE
-----------
{match_score}%


MATCHING SKILLS
---------------
{", ".join(matching_skills)}


MISSING SKILLS
--------------
{", ".join(missing_skills)}


CANDIDATE STRENGTHS
-------------------
"""

    for strength in strengths:

        text_report += (
            f"\n- {strength}"
        )


    text_report += """

AREAS TO IMPROVE
----------------
"""

    for area in areas:

        text_report += (
            f"\n- {area}"
        )


    text_report += """

RESUME SUGGESTIONS
------------------
"""

    for suggestion in suggestions:

        text_report += (
            f"\n- {suggestion}"
        )


    text_report += """

INTERVIEW QUESTIONS
-------------------
"""

    for number, question in enumerate(
        questions,
        start=1
    ):

        text_report += (
            f"\n{number}. {question}"
        )


    st.download_button(
        label="📄 Download Text Report",
        data=text_report,
        file_name="resume_analysis.txt",
        mime="text/plain"
    )


    # =================================================
    # RESUME CHAT
    # =================================================

    st.divider()

    st.header(
        "💬 Ask Questions About Your Resume"
    )

    st.write(
        "Ask follow-up questions about your resume, "
        "job description, skills or analysis."
    )


    # -------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -------------------------------------------------

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # -------------------------------------------------
    # CHAT INPUT
    # -------------------------------------------------

    user_question = st.chat_input(
        "Ask something about your resume..."
    )


    if user_question:

        with st.chat_message("user"):

            st.write(
                user_question
            )


        # Save user question

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )


        # =================================================
        # CHAT HISTORY TEXT
        # =================================================

        chat_history_text = ""

        for message in st.session_state.chat_history:

            chat_history_text += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )


        # =================================================
        # CHAT PROMPT
        # =================================================

        chat_prompt = f"""
You are an AI resume assistant.

Answer the user's question using the
resume, job description and analysis.

========================
RESUME
========================

{st.session_state.resume_text}

========================
JOB DESCRIPTION
========================

{st.session_state.job_description}

========================
MATCH SCORE
========================

{match_score}%

========================
MATCHING SKILLS
========================

{matching_skills}

========================
MISSING SKILLS
========================

{missing_skills}

========================
AI ANALYSIS
========================

{json.dumps(analysis, indent=2)}

========================
CHAT HISTORY
========================

{chat_history_text}

========================
CURRENT QUESTION
========================

{user_question}

========================
RULES
========================

1. Use the resume and job description
   as the main sources.

2. Do not invent experience.

3. Do not claim that the candidate has
   skills that are not in the resume.

4. Give practical answers.

5. If information is not available,
   say that clearly.
"""


        # =================================================
        # CALL GEMINI FOR CHAT
        # =================================================

        with st.spinner(
            "Thinking..."
        ):

            try:

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=chat_prompt
                )

                chat_answer = response.text


            except Exception as e:

                error_message = str(e)

                if "429" in error_message:

                    chat_answer = (
                        "⚠️ Gemini quota has been reached. "
                        "Please try again after the quota resets."
                    )

                elif "503" in error_message:

                    chat_answer = (
                        "⚠️ Gemini is temporarily busy. "
                        "Please try again later."
                    )

                else:

                    chat_answer = (
                        "⚠️ The AI service is "
                        "temporarily unavailable."
                    )


        # =================================================
        # DISPLAY CHAT ANSWER
        # =================================================

        with st.chat_message(
            "assistant"
        ):

            st.write(
                chat_answer
            )


        # Save response

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": chat_answer
            }
        )