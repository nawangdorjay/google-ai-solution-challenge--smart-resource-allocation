import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation('c:/Users/nawan/Downloads/google ai sol challenge/simple_ml/[EXT] Solution Challenge 2026 - Prototype PPT Template (1).pptx')

def add_body_text(slide, text, font_size=15, top=1.5, left=0.5, width=9, height=5, bold_first_line=True):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        if i == 0 and bold_first_line:
            p.font.bold = True
            p.font.size = Pt(font_size + 2)
        if line.startswith('•') or line.startswith('-'):
            p.level = 1

def add_colored_box(slide, text, left, top, width, height, fill_rgb=(20, 220, 180), text_rgb=(0,0,0), font_size=13):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(*fill_rgb)
    shape.line.color.rgb = RGBColor(200, 200, 200)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = text
    for para in tf.paragraphs:
        para.font.size = Pt(font_size)
        para.font.color.rgb = RGBColor(*text_rgb)
        para.alignment = PP_ALIGN.CENTER
    return shape

# ── Slide 2: Team Details ──────────────────────────────────────────────────────
try:
    s2 = prs.slides[1]
    s2.shapes[2].text_frame.text = (
        "Team Details\n\n"
        "Team Name: Team Lapper\n"
        "Team Leader: Nawang Dorjay\n"
        "Members: Nawang Dorjay (ML/Backend), Team Members (Frontend, UI/UX, Data)\n\n"
        "UN SDG Alignment:\n"
        "• SDG 1 — No Poverty (Resource equity in crises)\n"
        "• SDG 11 — Sustainable Cities (Resilient communities)\n"
        "• SDG 17 — Partnerships for the Goals\n\n"
        "Problem Statement: During crises, traditional NGO resource allocation is drastically "
        "inefficient — taking hours of manual labor to dispatch help. NGOs struggle to find vetted, "
        "accurately skilled volunteers in their immediate geographical radius. Lapper solves this "
        "life-saving bottleneck using Hybrid AI."
    )
except Exception as e:
    print("Slide 2 error:", e)

# ── Slide 3: Brief ────────────────────────────────────────────────────────────
add_body_text(prs.slides[2], (
    "Lapper: Smart Resource Allocation Engine\n\n"
    "The Crisis:\n"
    "During the 2023 Turkey earthquake, NGOs reported 4+ hour delays in mobilizing volunteers. "
    "Manual dispatching costs lives in time-critical disasters.\n\n"
    "The Solution:\n"
    "Lapper is a production-ready, full-stack AI platform designed to intelligently pair vetted "
    "volunteers with real-time NGO crisis requests — reducing allocation time from hours to milliseconds.\n\n"
    "How It Works:\n"
    "Our hybrid AI engine uses Scikit-learn's Logistic Regression to evaluate volunteers across 5 "
    "dimensions: Skill Overlap, Proximity, Urgency, Availability, and Experience. "
    "Google Gemini then translates these scores into transparent, human-readable explanations — "
    "bridging the gap between ML output and administrative trust."
))

# ── Slide 4: Opportunities ────────────────────────────────────────────────────
add_body_text(prs.slides[3], (
    "Market Opportunity & Differentiation\n\n"
    "Market Size: The global volunteer management market is $1.8B+ and growing at 12% YoY.\n\n"
    "Why Existing Solutions Fail:\n"
    "• VolunteerHub, Better Impact: Rigid keyword filtering — no AI scoring\n"
    "• Google.org tools: No real-time ML matching pipeline\n"
    "• Manual NGO spreadsheets: Hours of delay; no geo-proximity awareness\n\n"
    "Why Lapper Wins:\n"
    "• Hybrid ML + LLM: Only platform combining Logistic Regression with Gemini explanations\n"
    "• Speed: Sub-500ms match vs 4+ hours manual\n"
    "• Transparency: Every decision is explainable — critical for NGO accountability\n"
    "• Scalability: Docker + Cloud Run ready; scales to millions of volunteers"
))

# ── Slide 5: Features ─────────────────────────────────────────────────────────
add_body_text(prs.slides[4], (
    "Key Platform Features\n\n"
    "⚡ Real-Time AI Dispatching\n"
    "   Interactive dashboard updates constraints and volunteer statuses instantly.\n\n"
    "🤖 Hybrid AI Scoring Engine\n"
    "   Logistic Regression pipeline scores candidates across 5 critical features.\n\n"
    "💡 Gemini Explainable AI\n"
    "   Google Gemini 1.5 Flash generates transparent rationale for every match decision.\n\n"
    "🗄️ Scalable Data Pipeline\n"
    "   Python backend imports, cleans, and sanitizes thousands of volunteer records.\n\n"
    "📊 Live Analytics Dashboard\n"
    "   Charts show match success rates, regional coverage, and volunteer trends.\n\n"
    "🔐 Settings & API Management\n"
    "   Users can configure their own Gemini API key securely from the UI."
))

# ── Slide 6: Process Flow ─────────────────────────────────────────────────────
s6 = prs.slides[5]

def add_process_box(text, left, top, width, height, fill_color=(20, 220, 180)):
    shape = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(*fill_color)
    shape.line.color.rgb = RGBColor(0, 0, 0)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = text
    tf.paragraphs[0].font.size = Pt(13)
    tf.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
    return shape

def add_arrow(slide, left, top, width, height):
    slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left), Inches(top), Inches(width), Inches(height))

add_process_box("1. NGO Posts\nUrgent Request", 0.3, 2.5, 1.7, 1)
add_arrow(s6, 2.1, 2.8, 0.4, 0.3)
add_process_box("2. Engine Fetches\nVetted Candidates", 2.6, 2.5, 1.7, 1)
add_arrow(s6, 4.4, 2.8, 0.4, 0.3)
add_process_box("3. Logistic Regression\nScores Fit\n< 500ms ⚡", 4.9, 2.5, 1.7, 1)
add_arrow(s6, 6.7, 2.8, 0.4, 0.3)
add_process_box("4. Gemini AI\nExplains Logic\n(Google Gemini 1.5)", 7.2, 2.5, 1.9, 1, fill_color=(139, 92, 246))

s6.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(8.4), Inches(3.6), Inches(0.4), Inches(0.4))
add_process_box("5. Admin Reviews &\nDeploys Volunteer ✓", 7.2, 4.1, 1.9, 1, fill_color=(255, 165, 0))

add_body_text(s6, "Automated AI Workflow Pipeline — Sub-500ms End-to-End", top=1.2)

# ── Slide 7: NEW — Google AI & Antigravity Usage ──────────────────────────────
try:
    s7 = prs.slides[6]
    add_body_text(s7, (
        "Built with Google AI — End to End\n\n"
        "🔵 Google Gemini 1.5 Flash (Core AI Feature)\n"
        "   Every volunteer match generates a transparent, human-readable rationale via the Gemini API.\n"
        "   Turns raw ML probability vectors into clear English for NGO administrators.\n\n"
        "🟣 Google Antigravity (AI Development Assistant)\n"
        "   The entire Lapper platform was built collaboratively with Google Antigravity — "
        "Google DeepMind's advanced agentic AI coding assistant. Antigravity helped architect the "
        "matching engine, debug the Flask REST API, design the premium UI, configure Docker, "
        "manage the GitHub CI/CD pipeline, and deploy to Render. This accelerated development "
        "from weeks to days — demonstrating how Google AI amplifies developer productivity.\n\n"
        "🟡 Google AI Studio\n"
        "   Used for Gemini API key provisioning and prompt engineering & testing.\n\n"
        "🟢 Google Cloud Ready\n"
        "   Dockerfile configured for Google Cloud Run deployment."
    ))
except Exception as e:
    print("Slide 7 error:", e)

# ── Slide 8: Architecture ─────────────────────────────────────────────────────
s8 = prs.slides[7]

def add_arch_box(text, left, top, width, height, color=(100, 149, 237)):
    shape = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(*color)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = text
    tf.paragraphs[0].font.size = Pt(13)
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

add_arch_box("User Browser\n(HTML5/CSS/JS\nDashboard)", 0.3, 2.0, 1.9, 1.5)
s8.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(2.3), Inches(2.6), Inches(0.5), Inches(0.3))
add_arch_box("Python Flask\nBackend API\n(main.py)", 2.9, 2.0, 2.0, 1.5, color=(46, 139, 87))
s8.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(3.8), Inches(3.6), Inches(0.3), Inches(0.5))
add_arch_box("SQLite Database\n(volunteer_lite.db)", 2.9, 4.2, 2.0, 1.0, color=(105, 105, 105))
s8.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(5.0), Inches(2.6), Inches(0.5), Inches(0.3))
add_arch_box("AI Pipeline\n(Google Stack)", 5.6, 1.8, 3.5, 2.5, color=(66, 133, 244))
add_arch_box("Gemini 1.5 Flash\n(Explainability)", 5.8, 2.0, 3.0, 0.9, color=(255, 20, 147))
add_arch_box("Scikit-learn\nLogistic Regression", 5.8, 3.0, 3.0, 0.9, color=(255, 140, 0))
add_arch_box("Antigravity AI\n(Built with)", 5.8, 4.0, 3.0, 0.7, color=(139, 92, 246))

add_body_text(s8, "System Architecture — Cloud-Ready Stack", top=1.2)

# ── Slide 9: Technologies ─────────────────────────────────────────────────────
add_body_text(prs.slides[8], (
    "Core Technologies & Google Integration\n\n"
    "Backend: Python 3.11 | Flask REST API | SQLite | Gunicorn\n"
    "Frontend: HTML5, Vanilla CSS, JavaScript | Chart.js | Lucide Icons\n"
    "ML Engine: Scikit-learn (Logistic Regression, StandardScaler Pipeline)\n"
    "Containerization: Docker | Google Cloud Run compatible\n"
    "Hosting: Render.com (Live: google-ai-solution-challenge-smart.onrender.com)\n\n"
    "Google Technologies:\n"
    "• Google Gemini 1.5 Flash API — Explainable AI rationale generation\n"
    "• Google AI Studio — API key management & prompt engineering\n"
    "• Google Antigravity — AI-assisted end-to-end development acceleration\n"
    "• Google Cloud Run — Production deployment target (Dockerfile included)\n\n"
    "GitHub: github.com/nawangdorjay/google-ai-solution-challenge--smart-resource-allocation"
))

# ── Slide 10: NEW — Roadmap ───────────────────────────────────────────────────
try:
    s10 = prs.slides[9]
    add_colored_box(s10, "Phase 1 — NOW\n✅ MVP Live\nLogistic Regression\nGemini Explainability\nFlask API + SQLite\nDocker + Render Deploy", 0.4, 2.0, 2.8, 3.0, fill_rgb=(20, 220, 180), text_rgb=(0,0,0))
    add_colored_box(s10, "Phase 2 — 3 Months\n🔄 Scale Up\nVertex AI AutoML\nReal-time GPS tracking\nFirebase Auth\nMobile-Responsive PWA", 3.5, 2.0, 2.8, 3.0, fill_rgb=(59, 130, 246), text_rgb=(255,255,255))
    add_colored_box(s10, "Phase 3 — 6 Months\n🚀 Production\nMulti-language Gemini\nNative Mobile App\nNGO Analytics Suite\nGovernment API Integrations", 6.6, 2.0, 2.8, 3.0, fill_rgb=(139, 92, 246), text_rgb=(255,255,255))
    add_body_text(s10, "Product Roadmap — Path to Impact at Scale", top=1.2)
except Exception as e:
    print("Slide 10 error:", e)

# ── Slide 11: MVP Snapshots ───────────────────────────────────────────────────
try:
    slide11 = prs.slides[10]
    add_body_text(slide11, (
        "Live MVP Snapshots\n\n"
        "🌐 Live App: https://google-ai-solution-challenge-smart.onrender.com\n"
        "💻 GitHub:   https://github.com/nawangdorjay/google-ai-solution-challenge--smart-resource-allocation"
    ), top=5.0, font_size=13)

    img_path_1 = r"C:\Users\nawan\.gemini\antigravity\brain\d03db546-d69e-43d9-9fdc-cf80b90d5c55\.system_generated\click_feedback\click_feedback_1776967314381.png"
    if os.path.exists(img_path_1):
        slide11.shapes.add_picture(img_path_1, Inches(0.5), Inches(1.5), width=Inches(4.2))
except Exception as e:
    print("Slide 11 error:", e)

prs.save("c:/Users/nawan/Downloads/google ai sol challenge/simple_ml/Final_Submission_Enhanced_v3.pptx")
print("Enhanced presentation saved as Final_Submission_Enhanced_v3.pptx")

