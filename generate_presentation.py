import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_slide_layout = prs.slide_layouts[6]

# Color Palette (Dark Executive Theme matching Neumorphic Project Aesthetic)
C_BG_DARK = RGBColor(15, 23, 42)        # Slate 900
C_SURFACE = RGBColor(30, 41, 59)        # Slate 800
C_SURFACE_LIGHT = RGBColor(51, 65, 85)  # Slate 700
C_CYAN = RGBColor(6, 182, 212)          # Electric Cyan (Primary Brand)
C_EMERALD = RGBColor(16, 185, 129)      # Emerald Green (Reliability)
C_AMBER = RGBColor(245, 158, 11)        # Vibrant Amber (Warning/Alert)
C_VIOLET = RGBColor(139, 92, 246)       # Violet Accent
C_TEXT_WHITE = RGBColor(248, 250, 252)  # Crisp White
C_TEXT_MUTED = RGBColor(148, 163, 184)  # Light Slate Gray
C_TEXT_DIM = RGBColor(100, 116, 139)    # Muted Gray
C_BORDER = RGBColor(71, 85, 105)        # Slate 600

def set_slide_background(slide):
    """Fills slide background with dark executive navy."""
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG_DARK
    bg_shape.line.color.rgb = C_BG_DARK
    return bg_shape

def add_header(slide, category, title, slide_num=None):
    """Adds uniform high-visibility header to slide with large typography."""
    # Category Tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.size = Pt(13)
    p_c.font.bold = True
    p_c.font.color.rgb = C_CYAN

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_WHITE

    # Slide Number pill on top-right
    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(1.0), Inches(0.4))
        tf_n = num_box.text_frame
        tf_n.margin_left = tf_n.margin_right = tf_n.margin_top = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.text = f"{slide_num:02d} / 15"
        p_n.font.size = Pt(13)
        p_n.font.bold = True
        p_n.font.color.rgb = C_TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=C_SURFACE, border_color=C_BORDER):
    """Creates a sleek elevated container panel."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card

# ==============================================================================
# SLIDE 1: Title & Vision
# ==============================================================================
s1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s1)

# Center decorative card
c1 = add_card(s1, 1.0, 1.0, 11.333, 5.5, bg_color=C_SURFACE, border_color=C_CYAN)

tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.333), Inches(4.7))
tf1 = tb1.text_frame
tf1.word_wrap = True

p1_badge = tf1.paragraphs[0]
p1_badge.text = "CAPSTONE INNOVATION & COMMUTE RECOVERY ENGINE"
p1_badge.font.size = Pt(14)
p1_badge.font.bold = True
p1_badge.font.color.rgb = C_CYAN

p1_title = tf1.add_paragraph()
p1_title.text = "Mobility Recovery Engine"
p1_title.font.size = Pt(46)
p1_title.font.bold = True
p1_title.font.color.rgb = C_TEXT_WHITE
p1_title.space_before = Pt(8)

p1_sub = tf1.add_paragraph()
p1_sub.text = "Deadline-Driven Route Recovery & Stochastic Arrival Reliability Platform"
p1_sub.font.size = Pt(22)
p1_sub.font.bold = True
p1_sub.font.color.rgb = C_EMERALD
p1_sub.space_before = Pt(6)

p1_desc = tf1.add_paragraph()
p1_desc.text = "A full-stack, zero-cost intelligence system designed for students and working professionals. Instead of only computing the shortest path, it calculates the route with the highest probability of arriving before a strict deadline, backed by 1,000-run Monte Carlo simulations, A* road heuristics, and live recovery plans."
p1_desc.font.size = Pt(16)
p1_desc.font.color.rgb = C_TEXT_MUTED
p1_desc.space_before = Pt(14)

p1_meta = tf1.add_paragraph()
p1_meta.text = "KEY PILLARS: Pan-India A* Multi-Routing  •  Monte Carlo Simulation  •  Latest Safe Departure Countdown  •  Offline PWA"
p1_meta.font.size = Pt(14)
p1_meta.font.bold = True
p1_meta.font.color.rgb = C_AMBER
p1_meta.space_before = Pt(22)

# ==============================================================================
# SLIDE 2: The Core Problem & Commuter Dilemma
# ==============================================================================
s2 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s2)
add_header(s2, "Problem Statement & Commuter Reality", "Why Conventional GPS Fails Deadline-Bound Commuters", 2)

col_w = 3.6
gap = 0.25
top_pos = 1.6
card_h = 4.4

problems = [
    {
        "title": "The Average-Time Illusion",
        "color": C_AMBER,
        "points": [
            "Apps like Google Maps optimize only for static average or shortest distance.",
            "They assume constant road conditions, ignoring transit delay variance and traffic volatility.",
            "A 10-minute unexpected bottleneck cascades into missed connections and ruined schedules."
        ]
    },
    {
        "title": "The Brutal Cost of Being Late",
        "color": RGBColor(239, 68, 68),
        "points": [
            "University students face strict 75% attendance cutoffs and locked exam hall doors.",
            "Working adults face salary deductions, missed client meetings, and disciplinary marks.",
            "Commuters suffer severe stress and anxiety over unpredictable bus and train timings."
        ]
    },
    {
        "title": "Zero Proactive Recovery",
        "color": C_CYAN,
        "points": [
            "Current apps never provide a 'Latest Safe Departure (LSD)' countdown.",
            "When a commuter is running late or misses a transit leg, existing tools leave them stranded.",
            "Commuters need guaranteed probability of on-time arrival, not just nominal travel minutes."
        ]
    }
]

for i, p in enumerate(problems):
    left = 0.8 + i * (col_w + gap)
    add_card(s2, left, top_pos, col_w, card_h, border_color=p["color"])
    tb = s2.shapes.add_textbox(Inches(left + 0.2), Inches(top_pos + 0.2), Inches(col_w - 0.4), Inches(card_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = p["title"]
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = p["color"]
    
    for pt in p["points"]:
        p_b = tf.add_paragraph()
        p_b.text = f"• {pt}"
        p_b.font.size = Pt(15)
        p_b.font.color.rgb = C_TEXT_WHITE
        p_b.space_before = Pt(12)

# Bottom callout
callout = s2.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.8))
tf_c = callout.text_frame
p_c = tf_c.paragraphs[0]
p_c.text = "THE CORE QUESTION: Conventional GPS answers 'Which route is shortest?' — Commuters urgently need: 'Will I make it before my hard deadline?'"
p_c.font.size = Pt(15)
p_c.font.bold = True
p_c.font.color.rgb = C_EMERALD

# ==============================================================================
# SLIDE 3: Buyer Persona
# ==============================================================================
s3 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s3)
add_header(s3, "User Research & Target Audience", "Target Personas: Who Needs This Engine Most?", 3)

personas = [
    {
        "name": "Persona 1: Rahul Sharma (21)",
        "tag": "COLLEGE STUDENT (VIT VELLORE)",
        "color": C_CYAN,
        "rows": [
            ("Daily Context", "Commutes between Katpadi, Arani & Tiruvannamalai for labs & exams."),
            ("Critical Pain", "Zero tolerance for being late. 75% attendance rule means 1 late arrival blocks semester credits."),
            ("Transit Reality", "Relies on Tamil Nadu State buses and trains with unpredictable delay spreads (+/- 25 mins)."),
            ("Primary Need", "Needs a countdown to the 'Latest Safe Departure' and an instant backup route if a bus is missed.")
        ]
    },
    {
        "name": "Persona 2: Priya Menon (28)",
        "tag": "WORKING PROFESSIONAL & REGULAR COMMUTER",
        "color": C_EMERALD,
        "rows": [
            ("Daily Context", "Daily office commuter across regional highway corridors and city transit."),
            ("Critical Pain", "Biometric punch-in at 9:15 AM sharp. Accidental touches on GPS phone reroute her into traffic bottlenecks."),
            ("Transit Reality", "Switches between car driving and bus transit depending on peak congestion."),
            ("Primary Need", "Route locking protection against accidental screen taps, and side-by-side arrival probability comparison.")
        ]
    }
]

for i, pers in enumerate(personas):
    left = 0.8 + i * (5.7 + 0.33)
    add_card(s3, left, 1.6, 5.7, 5.2, border_color=pers["color"])
    tb = s3.shapes.add_textbox(Inches(left + 0.3), Inches(1.8), Inches(5.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = pers["name"]
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_WHITE
    
    p_tag = tf.add_paragraph()
    p_tag.text = pers["tag"]
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = pers["color"]
    p_tag.space_before = Pt(4)
    
    for lbl, val in pers["rows"]:
        p_row = tf.add_paragraph()
        p_row.text = f"{lbl}: "
        p_row.font.bold = True
        p_row.font.size = Pt(15)
        p_row.font.color.rgb = C_AMBER
        p_row.space_before = Pt(10)
        
        # Add value text
        run = p_row.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = C_TEXT_WHITE

# ==============================================================================
# SLIDE 4: Empathy Map
# ==============================================================================
s4 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s4)
add_header(s4, "Design Thinking & User Empathy", "Empathy Map: The Emotional Journey of Late Commuters", 4)

quadrants = [
    {
        "title": "THINKS",
        "color": C_CYAN,
        "items": [
            "\"Google Maps says 50 mins, but it always takes 75 mins in reality.\"",
            "\"If I miss the 8:15 bus, what is my emergency plan?\"",
            "\"I wonder how much safety buffer I actually have before the deadline.\""
        ]
    },
    {
        "title": "FEELS",
        "color": RGBColor(239, 68, 68),
        "items": [
            "Severe anxiety watching the digital clock tick closer to the deadline.",
            "Frustration when unannounced traffic delays ruin an entire day's plans.",
            "Helplessness when relying on infrequent transit with zero recovery advice."
        ]
    },
    {
        "title": "SAYS",
        "color": C_EMERALD,
        "items": [
            "\"I cannot afford to be even 5 minutes late today!\"",
            "\"Is there a reliable alternative highway, even if it's slightly longer?\"",
            "\"Tell me the latest time I can leave my house safely!\""
        ]
    },
    {
        "title": "DOES",
        "color": C_AMBER,
        "items": [
            "Constantly checks clock while rushing through breakfast or meetings.",
            "Takes reckless, high-risk detours in panic when stuck behind a truck.",
            "Reroutes phone by mistake due to sweaty hands or accidental screen touches."
        ]
    }
]

q_w = 5.7
q_h = 2.4
positions = [
    (0.8, 1.6), (6.833, 1.6),
    (0.8, 4.3), (6.833, 4.3)
]

for idx, (l, t) in enumerate(positions):
    q = quadrants[idx]
    add_card(s4, l, t, q_w, q_h, border_color=q["color"])
    tb = s4.shapes.add_textbox(Inches(l + 0.25), Inches(t + 0.15), Inches(q_w - 0.5), Inches(q_h - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = q["title"]
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = q["color"]
    
    for itm in q["items"]:
        p_b = tf.add_paragraph()
        p_b.text = f"• {itm}"
        p_b.font.size = Pt(14)
        p_b.font.color.rgb = C_TEXT_WHITE
        p_b.space_before = Pt(4)

# ==============================================================================
# SLIDE 5: Value Proposition Canvas
# ==============================================================================
s5 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s5)
add_header(s5, "Product-Market Fit", "Value Proposition Canvas: Aligning Customer Needs to Solution", 5)

add_card(s5, 0.8, 1.6, 5.7, 5.2, border_color=C_AMBER)
tb_left = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.9))
tf_l = tb_left.text_frame
tf_l.word_wrap = True

p_lh = tf_l.paragraphs[0]
p_lh.text = "CUSTOMER PROFILE (Needs & Friction)"
p_lh.font.size = Pt(20)
p_lh.font.bold = True
p_lh.font.color.rgb = C_AMBER

p_cj = tf_l.add_paragraph()
p_cj.text = "CUSTOMER JOBS:"
p_cj.font.size = Pt(16)
p_cj.font.bold = True
p_cj.font.color.rgb = C_TEXT_WHITE
p_cj.space_before = Pt(8)

p_cj_b = tf_l.add_paragraph()
p_cj_b.text = "• Arrive at exams, offices, or labs strictly before deadline.\n• Select optimal transport mode (Car, Bus, Train).\n• Maintain safety buffer against unexpected road gridlocks."
p_cj_b.font.size = Pt(14)
p_cj_b.font.color.rgb = C_TEXT_MUTED

p_cp = tf_l.add_paragraph()
p_cp.text = "CUSTOMER PAINS:"
p_cp.font.size = Pt(16)
p_cp.font.bold = True
p_cp.font.color.rgb = RGBColor(239, 68, 68)
p_cp.space_before = Pt(10)

p_cp_b = tf_l.add_paragraph()
p_cp_b.text = "• Misleading 'nominal' travel times that ignore variability.\n• Zero recovery advice when late or when a connection is missed.\n• App freezes and lost routes during patchy internet in transit."
p_cp_b.font.size = Pt(14)
p_cp_b.font.color.rgb = C_TEXT_MUTED

# Right Side: Value Map
add_card(s5, 6.833, 1.6, 5.7, 5.2, border_color=C_CYAN)
tb_right = s5.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.9))
tf_r = tb_right.text_frame
tf_r.word_wrap = True

p_rh = tf_r.paragraphs[0]
p_rh.text = "VALUE MAP (Our Recovery Engine)"
p_rh.font.size = Pt(20)
p_rh.font.bold = True
p_rh.font.color.rgb = C_CYAN

p_pr = tf_r.add_paragraph()
p_pr.text = "PRODUCTS & SERVICES:"
p_pr.font.size = Pt(16)
p_pr.font.bold = True
p_pr.font.color.rgb = C_TEXT_WHITE
p_pr.space_before = Pt(8)

p_pr_b = tf_r.add_paragraph()
p_pr_b.text = "• Full-Stack PWA Mobility Recovery Engine with A* Multi-Routing.\n• 1,000-run Monte Carlo Stochastic Engine evaluating arrival probability."
p_pr_b.font.size = Pt(14)
p_pr_b.font.color.rgb = C_TEXT_MUTED

p_rel = tf_r.add_paragraph()
p_rel.text = "PAIN RELIEVERS & GAIN CREATORS:"
p_rel.font.size = Pt(16)
p_rel.font.bold = True
p_rel.font.color.rgb = C_EMERALD
p_rel.space_before = Pt(10)

p_rel_b = tf_r.add_paragraph()
p_rel_b.text = "• Proactive Latest Safe Departure (LSD) with live countdown timer.\n• Automatic Contingency Plan: Best backup route if transit is missed.\n• Offline-first Service Worker cache for zero-connection reliability.\n• One-touch Route Locking with confirmation modal."
p_rel_b.font.size = Pt(14)
p_rel_b.font.color.rgb = C_TEXT_MUTED

# ==============================================================================
# SLIDE 6: Minimum Viable Product (MVP) Scope
# ==============================================================================
s6 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s6)
add_header(s6, "Product Architecture & Scope", "Minimum Viable Product (MVP): Delivered Capabilities", 6)

mvp_pillars = [
    {
        "num": "01",
        "title": "A* Routing & Diverse Alternatives",
        "color": C_CYAN,
        "desc": "Pan-India graph routing using OSMnx/OSRM + Haversine heuristic. Penalty method generates >= 3 diverse alternatives with <80% overlap filter."
    },
    {
        "num": "02",
        "title": "Monte Carlo Reliability Engine",
        "color": C_EMERALD,
        "desc": "1,000 iterations per route simulating Gaussian travel distributions. Calculates exact On-Time Probability (OTP %), Expected & P90 Arrival."
    },
    {
        "num": "03",
        "title": "Recovery & Latest Safe Departure",
        "color": C_AMBER,
        "desc": "Dynamic status classification (Can Make It / Risky / Cannot). Live countdown to Latest Safe Departure (LSD) and missed-transit contingency."
    },
    {
        "num": "04",
        "title": "PWA Offline & Route Lock Protection",
        "color": C_VIOLET,
        "desc": "Progressive Web App with Service Worker for offline commute tracking. Touch confirmation lock protects against accidental rerouting while moving."
    }
]

card_w6 = 5.7
card_h6 = 2.4
coords6 = [(0.8, 1.6), (6.833, 1.6), (0.8, 4.3), (6.833, 4.3)]

for idx, (l, t) in enumerate(coords6):
    m = mvp_pillars[idx]
    add_card(s6, l, t, card_w6, card_h6, border_color=m["color"])
    tb = s6.shapes.add_textbox(Inches(l + 0.25), Inches(t + 0.15), Inches(card_w6 - 0.5), Inches(card_h6 - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_num = tf.paragraphs[0]
    p_num.text = f"FEATURE PILLAR {m['num']}: {m['title'].upper()}"
    p_num.font.size = Pt(16)
    p_num.font.bold = True
    p_num.font.color.rgb = m["color"]
    
    p_d = tf.add_paragraph()
    p_d.text = m["desc"]
    p_d.font.size = Pt(15)
    p_d.font.color.rgb = C_TEXT_WHITE
    p_d.space_before = Pt(8)

# ==============================================================================
# SLIDE 7: How Our App Works (Step-by-Step Flow)
# ==============================================================================
s7 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s7)
add_header(s7, "User Experience & Workflow", "How Our App Works: 4-Step Commuter Journey", 7)

steps = [
    {
        "step": "STEP 1",
        "title": "Trip Setup & Deadline",
        "color": C_CYAN,
        "details": [
            "Type source & destination anywhere in India or drop pins on interactive map.",
            "Enter current departure time and hard arrival deadline.",
            "Select transit mode: Driving/Cab, Bus Transit, Train/Rail, or All Modes."
        ]
    },
    {
        "step": "STEP 2",
        "title": "Multi-Corridor Routing",
        "color": C_EMERALD,
        "details": [
            "Engine computes 1 shortest route + 3 distinct alternative corridors.",
            "Penalty method inflates costs on used edges to force non-overlapping paths.",
            "Strict <80% path overlap filter eliminates cosmetic redundant detours."
        ]
    },
    {
        "step": "STEP 3",
        "title": "Monte Carlo Simulation",
        "color": C_AMBER,
        "details": [
            "Runs 1,000 iterations per route drawing from empirical variance data.",
            "Computes On-Time Probability (OTP %) and 90th percentile arrival (P90).",
            "Derives Latest Safe Departure (LSD) with real-time countdown."
        ]
    },
    {
        "step": "STEP 4",
        "title": "Side-by-Side Lock & Go",
        "color": C_VIOLET,
        "details": [
            "Inspect candidate routes side-by-side with dedicated individual maps.",
            "Confirm & Lock route to prevent accidental touch rerouting during transit.",
            "If transit delay occurs, engine instantly triggers missed-transit fallback."
        ]
    }
]

step_w = 2.75
step_gap = 0.24
for i, s in enumerate(steps):
    left = 0.8 + i * (step_w + step_gap)
    add_card(s7, left, 1.6, step_w, 5.2, border_color=s["color"])
    tb = s7.shapes.add_textbox(Inches(left + 0.15), Inches(1.8), Inches(step_w - 0.3), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_step = tf.paragraphs[0]
    p_step.text = s["step"]
    p_step.font.size = Pt(14)
    p_step.font.bold = True
    p_step.font.color.rgb = s["color"]
    
    p_t = tf.add_paragraph()
    p_t.text = s["title"]
    p_t.font.size = Pt(18)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_WHITE
    p_t.space_before = Pt(4)
    
    for d in s["details"]:
        p_d = tf.add_paragraph()
        p_d.text = f"• {d}"
        p_d.font.size = Pt(14)
        p_d.font.color.rgb = C_TEXT_MUTED
        p_d.space_before = Pt(10)

# ==============================================================================
# SLIDE 8: System Architecture & Tech Stack
# ==============================================================================
s8 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s8)
add_header(s8, "Engineering Foundation", "4-Tier Full-Stack System Architecture", 8)

tiers = [
    {
        "layer": "TIER 1: CLIENT PRESENTATION (PWA)",
        "tech": "React 18 + Vite  •  Plain Neumorphic CSS  •  Leaflet.js  •  Service Worker",
        "color": C_CYAN,
        "desc": "Mobile-first tactile UI. Features side-by-side route maps, live LSD countdown timer, interactive pin-picker, and PWA cache for zero-connectivity offline operation."
    },
    {
        "layer": "TIER 2: API GATEWAY & CONTROLLER",
        "tech": "FastAPI (Python 3)  •  Uvicorn ASGI  •  Pydantic Schemas  •  CORS Middleware",
        "color": C_EMERALD,
        "desc": "High-throughput asynchronous REST API providing /plan, /lock, /log, /history, /geocode, and /health endpoints with automated OpenAPI interactive documentation."
    },
    {
        "layer": "TIER 3: COMPUTATIONAL ENGINE & ROUTING CORE",
        "tech": "NetworkX  •  OSMNx  •  NumPy  •  A* Heuristic Search  •  OSRM Engine",
        "color": C_AMBER,
        "desc": "Downloads & caches regional road networks (.graphml). Executes A* search with Haversine distance heuristic, penalty-based alternative generator, and 1,000-run Monte Carlo simulation."
    },
    {
        "layer": "TIER 4: DATA PERSISTENCE & LEARNING LOOP",
        "tech": "SQLite Database  •  SQLAlchemy ORM  •  Welford's Statistical ML Algorithm",
        "color": C_VIOLET,
        "desc": "Stores TripLogs, LockedRoutes, and SegmentMetrics. Uses Bayesian incremental updating to calibrate segment mean travel times (mu) and variance (sigma) from real trip records."
    }
]

for idx, tr in enumerate(tiers):
    top = 1.6 + idx * 1.35
    add_card(s8, 0.8, top, 11.733, 1.2, border_color=tr["color"])
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(top + 0.1), Inches(11.333), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_l = tf.paragraphs[0]
    p_l.text = tr["layer"]
    p_l.font.size = Pt(16)
    p_l.font.bold = True
    p_l.font.color.rgb = tr["color"]
    
    run_tech = p_l.add_run()
    run_tech.text = f"   [{tr['tech']}]"
    run_tech.font.size = Pt(13)
    run_tech.font.bold = False
    run_tech.font.color.rgb = C_TEXT_MUTED
    
    p_d = tf.add_paragraph()
    p_d.text = tr["desc"]
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = C_TEXT_WHITE
    p_d.space_before = Pt(4)

# ==============================================================================
# SLIDE 9: Algorithmic Innovation: A* & Alternatives
# ==============================================================================
s9 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s9)
add_header(s9, "Algorithmic Innovation", "A* Road Routing & Penalty-Based Diverse Alternatives", 9)

add_card(s9, 0.8, 1.6, 5.7, 5.2, border_color=C_CYAN)
tb9_l = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.8))
tf9_l = tb9_l.text_frame
tf9_l.word_wrap = True

p9_lh = tf9_l.paragraphs[0]
p9_lh.text = "ADMISSIBLE A* ROAD ROUTING"
p9_lh.font.size = Pt(20)
p9_lh.font.bold = True
p9_lh.font.color.rgb = C_CYAN

p9_l1 = tf9_l.add_paragraph()
p9_l1.text = "1. Haversine Distance Heuristic:"
p9_l1.font.size = Pt(16)
p9_l1.font.bold = True
p9_l1.font.color.rgb = C_TEXT_WHITE
p9_l1.space_before = Pt(8)

p9_l1_d = tf9_l.add_paragraph()
p9_l1_d.text = "h(u, v) = Haversine(u, v) / Max_Speed (80 km/h)\nBy dividing the great-circle spherical distance by maximum permissible velocity, the heuristic is mathematically guaranteed to be ADMISSIBLE (never overestimates travel time), yielding the provably shortest road path."
p9_l1_d.font.size = Pt(14)
p9_l1_d.font.color.rgb = C_TEXT_MUTED

p9_l2 = tf9_l.add_paragraph()
p9_l2.text = "2. Graph Optimization:"
p9_l2.font.size = Pt(16)
p9_l2.font.bold = True
p9_l2.font.color.rgb = C_TEXT_WHITE
p9_l2.space_before = Pt(12)

p9_l2_d = tf9_l.add_paragraph()
p9_l2_d.text = "Pre-loads and caches regional road graphs (Vellore-Tiruvannamalai) into memory via GraphML. Uses fast spatial k-d tree lookup to snap GPS coordinates to the nearest road network node."
p9_l2_d.font.size = Pt(14)
p9_l2_d.font.color.rgb = C_TEXT_MUTED

# Right Side: Penalty Method
add_card(s9, 6.833, 1.6, 5.7, 5.2, border_color=C_EMERALD)
tb9_r = s9.shapes.add_textbox(Inches(7.033), Inches(1.8), Inches(5.3), Inches(4.8))
tf9_r = tb9_r.text_frame
tf9_r.word_wrap = True

p9_rh = tf9_r.paragraphs[0]
p9_rh.text = "PENALTY-BASED ALTERNATIVE GENERATION"
p9_rh.font.size = Pt(20)
p9_rh.font.bold = True
p9_rh.font.color.rgb = C_EMERALD

p9_r1 = tf9_r.add_paragraph()
p9_r1.text = "1. Iterative Edge Cost Inflation:"
p9_r1.font.size = Pt(16)
p9_r1.font.bold = True
p9_r1.font.color.rgb = C_TEXT_WHITE
p9_r1.space_before = Pt(8)

p9_r1_d = tf9_r.add_paragraph()
p9_r1_d.text = "Cost'(e) = Cost(e) * (1 + Penalty_Factor)\nEdges traversed by the primary route are penalized by 30-50%. Running A* on the modified graph forces the search into distinct highway and state bypass corridors."
p9_r1_d.font.size = Pt(14)
p9_r1_d.font.color.rgb = C_TEXT_MUTED

p9_r2 = tf9_r.add_paragraph()
p9_r2.text = "2. Strict Overlap Rejection Filter (< 80%):"
p9_r2.font.size = Pt(16)
p9_r2.font.bold = True
p9_r2.font.color.rgb = C_TEXT_WHITE
p9_r2.space_before = Pt(12)

p9_r2_d = tf9_r.add_paragraph()
p9_r2_d.text = "Calculates path edge overlap against previously accepted routes. Any candidate route sharing > 80% path length is strictly REJECTED, ensuring commuters get truly independent physical alternatives."
p9_r2_d.font.size = Pt(14)
p9_r2_d.font.color.rgb = C_TEXT_MUTED

# ==============================================================================
# SLIDE 10: Stochastic Simulation & Reliability Formula
# ==============================================================================
s10 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s10)
add_header(s10, "Mathematical Modeling", "Stochastic Monte Carlo Simulation & Reliability Scoring", 10)

col10_w = 3.6
gap10 = 0.25

cards10 = [
    {
        "title": "Monte Carlo Engine (1,000 Runs)",
        "color": C_CYAN,
        "bullets": [
            "Every road segment has an expected duration (mu) and variance (sigma).",
            "Simulates 1,000 independent random commuter journeys per route.",
            "Captures unexpected traffic bottlenecks, railway crossings, and peak rush delays."
        ]
    },
    {
        "title": "On-Time Probability & P90 Arrival",
        "color": C_EMERALD,
        "bullets": [
            "OTP % = (Runs arriving before deadline / 1,000) * 100%.",
            "P90 Arrival Time: The arrival time guaranteed in 90% of simulated journeys.",
            "Latest Safe Departure (LSD) = Deadline - P90 Travel Duration."
        ]
    },
    {
        "title": "Reliability Scoring Formula",
        "color": C_AMBER,
        "bullets": [
            "Score = Buffer - (w1 * Variability) - (w2 * Wait Time) - (w3 * Transfers)",
            "Configurable weights in config.py prioritize arrival buffer and penalize schedule instability.",
            "Gives commuters a single, actionable 0-100 reliability index for instant decision-making."
        ]
    }
]

for i, c in enumerate(cards10):
    left = 0.8 + i * (col10_w + gap10)
    add_card(s10, left, 1.6, col10_w, 4.4, border_color=c["color"])
    tb = s10.shapes.add_textbox(Inches(left + 0.2), Inches(1.8), Inches(col10_w - 0.4), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = c["title"]
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = c["color"]
    
    for b in c["bullets"]:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(15)
        p_b.font.color.rgb = C_TEXT_WHITE
        p_b.space_before = Pt(12)

# Bottom Formula Banner
bf = s10.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.8))
tf_bf = bf.text_frame
p_bf = tf_bf.paragraphs[0]
p_bf.text = "MATHEMATICAL ASSURANCE: Commuters never depend on 'best-case' estimates — they get statistical proof of on-time arrival before stepping out of the door."
p_bf.font.size = Pt(15)
p_bf.font.bold = True
p_bf.font.color.rgb = C_TEXT_WHITE

# ==============================================================================
# SLIDE 11: Machine Learning & Continuous Learning Loop
# ==============================================================================
s11 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s11)
add_header(s11, "Machine Learning & Self-Calibration", "The Self-Calibrating Commute: Bayesian Feedback Loop", 11)

ml_steps = [
    {
        "num": "STEP 1",
        "title": "Empirical Trip Telemetry",
        "color": C_CYAN,
        "desc": "Commuters log actual departure & arrival times via the /log endpoint. Trip logs record predicted duration vs actual road transit time, capturing seasonal bottlenecks."
    },
    {
        "num": "STEP 2",
        "title": "Welford's Online Algorithm",
        "color": C_EMERALD,
        "desc": "Updates running segment mean (mu) and variance (sigma^2) in a single pass without re-training heavy neural networks: M_k = M_{k-1} + (x_k - M_{k-1})/k. Prevents numerical instability."
    },
    {
        "num": "STEP 3",
        "title": "Adaptive Hyper-Local Intelligence",
        "color": C_AMBER,
        "desc": "As more commuters log trips, simulation accuracy increases automatically. Regional road works, monsoon delays, and checkpoint slowdowns reflect dynamically in future OTP % scores."
    }
]

for idx, ms in enumerate(ml_steps):
    left = 0.8 + idx * (3.75 + 0.24)
    add_card(s11, left, 1.6, 3.75, 4.4, border_color=ms["color"])
    tb = s11.shapes.add_textbox(Inches(left + 0.2), Inches(1.8), Inches(3.35), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_num = tf.paragraphs[0]
    p_num.text = ms["num"]
    p_num.font.size = Pt(14)
    p_num.font.bold = True
    p_num.font.color.rgb = ms["color"]
    
    p_t = tf.add_paragraph()
    p_t.text = ms["title"]
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_WHITE
    p_t.space_before = Pt(4)
    
    p_d = tf.add_paragraph()
    p_d.text = ms["desc"]
    p_d.font.size = Pt(15)
    p_d.font.color.rgb = C_TEXT_MUTED
    p_d.space_before = Pt(12)

# Bottom note
bn = s11.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.8))
tf_bn = bn.text_frame
p_bn = tf_bn.paragraphs[0]
p_bn.text = "DATA PRIVACY BY DESIGN: All trip calibration is aggregated locally into SQLite segment metrics — zero personal movement tracking or third-party ad profiling."
p_bn.font.size = Pt(15)
p_bn.font.bold = True
p_bn.font.color.rgb = C_CYAN

# ==============================================================================
# SLIDE 12: Business Model Canvas (BMC)
# ==============================================================================
s12 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s12)
add_header(s12, "Commercial Viability", "Business Model Canvas (BMC)", 12)

# 3x3 Grid for Business Model Canvas
bmc_blocks = [
    ("Key Partners", "• State Transit (TNSTC, Southern Railways)\n• Universities (VIT, Anna Univ)\n• OpenStreetMap contributors\n• Tech park shuttle operators", C_CYAN),
    ("Key Activities", "• Road graph caching & A* routing\n• 1,000-run Monte Carlo simulation\n• PWA offline engine updates\n• Bayesian variance calibration", C_EMERALD),
    ("Value Propositions", "• Guaranteed arrival probability (OTP %)\n• Proactive Latest Safe Departure (LSD)\n• Missed-transit contingency plans\n• 100% Zero Paid API costs", C_AMBER),
    ("Customer Relationships", "• Automated self-service PWA\n• Community trip verification logs\n• Zero intrusive tracking or ads\n• Touch-protected route locking", C_CYAN),
    ("Customer Segments", "• University Students (75% attendance)\n• Shift workers & healthcare staff\n• Daily corporate office commuters\n• Regional intercity travelers", C_EMERALD),
    ("Channels", "• Direct Web PWA (Zero app-store friction)\n• University student portals\n• Campus commuter ambassadors\n• Word-of-mouth student groups", C_AMBER),
    ("Key Resources", "• Cached OSMnx road graphs\n• Proprietary reliability algorithms\n• SQLite historical telemetry\n• FastAPI & React PWA codebase", C_VIOLET),
    ("Cost Structure", "• Ultra-low server hosting (FastAPI/SQLite)\n• Free OSM vector map tiles\n• Zero paid third-party API keys\n• Minimal devops & maintenance", C_VIOLET),
    ("Revenue Streams", "• B2B University Campus Attendance SaaS\n• Corporate Tech Park Commute Portals\n• Premium dynamic crowd-congestion alerts\n• Enterprise API licensing for transit fleets", C_VIOLET)
]

b_w = 3.75
b_h = 1.6
b_gap_x = 0.24
b_gap_y = 0.15

for idx, (title, content, col) in enumerate(bmc_blocks):
    row = idx // 3
    col_idx = idx % 3
    bx = 0.8 + col_idx * (b_w + b_gap_x)
    by = 1.6 + row * (b_h + b_gap_y)
    
    add_card(s12, bx, by, b_w, b_h, border_color=col)
    tb = s12.shapes.add_textbox(Inches(bx + 0.15), Inches(by + 0.1), Inches(b_w - 0.3), Inches(b_h - 0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = title.upper()
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = col
    
    p_c = tf.add_paragraph()
    p_c.text = content
    p_c.font.size = Pt(11)
    p_c.font.color.rgb = C_TEXT_WHITE
    p_c.space_before = Pt(3)

# ==============================================================================
# SLIDE 13: Go-To-Market (GTM) Strategy
# ==============================================================================
s13 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s13)
add_header(s13, "Market Rollout & Growth", "Go-To-Market (GTM) Strategy: 3-Phase Execution", 13)

gtm_phases = [
    {
        "phase": "PHASE 1 (MONTHS 1–3)",
        "name": "Hyper-Local Campus Beachhead",
        "color": C_CYAN,
        "bullets": [
            "Launch along the Katpadi – Vellore – Tiruvannamalai student corridor.",
            "Target: 5,000 active student users facing strict morning 8:00 AM lab cutoffs.",
            "Validate student attendance improvement and build core road variance dataset.",
            "Zero download friction: Share direct PWA web link across campus student groups."
        ]
    },
    {
        "phase": "PHASE 2 (MONTHS 4–8)",
        "name": "High-Density Commute Expansion",
        "color": C_EMERALD,
        "bullets": [
            "Scale to major Indian commute corridors: Chennai-Bengaluru, Mumbai-Pune.",
            "Integrate public transit GTFS timetables for Suburban Trains and State Buses.",
            "Launch crowdsourced trip logging incentives to reward accurate delay reports.",
            "Introduce multi-modal cab + transit dynamic split routing."
        ]
    },
    {
        "phase": "PHASE 3 (MONTHS 9–12)",
        "name": "B2B Enterprise & Institutional Licensing",
        "color": C_AMBER,
        "bullets": [
            "Partner with IT Parks (OMR Chennai, Whitefield Bengaluru) for employee arrival tracking.",
            "Offer universities customized White-Label Attendance Protection Portals.",
            "Monetize corporate shuttle route optimization and fleet reliability analytics.",
            "Position Mobility Recovery Engine as India's gold standard in punctual transit."
        ]
    }
]

gtm_w = 3.75
gtm_gap = 0.24
for i, g in enumerate(gtm_phases):
    left = 0.8 + i * (gtm_w + gtm_gap)
    add_card(s13, left, 1.6, gtm_w, 5.2, border_color=g["color"])
    tb = s13.shapes.add_textbox(Inches(left + 0.2), Inches(1.8), Inches(gtm_w - 0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_ph = tf.paragraphs[0]
    p_ph.text = g["phase"]
    p_ph.font.size = Pt(14)
    p_ph.font.bold = True
    p_ph.font.color.rgb = g["color"]
    
    p_t = tf.add_paragraph()
    p_t.text = g["name"]
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_WHITE
    p_t.space_before = Pt(4)
    
    for b in g["bullets"]:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(14)
        p_b.font.color.rgb = C_TEXT_MUTED
        p_b.space_before = Pt(10)

# ==============================================================================
# SLIDE 14: Competitive Advantage Matrix
# ==============================================================================
s14 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s14)
add_header(s14, "Market Differentiation", "Competitive Landscape: Why We Stand Out", 14)

# Table comparing Google Maps, Moovit, and Mobility Recovery Engine
rows_data = [
    ("FEATURE / CAPABILITY", "GOOGLE / APPLE MAPS", "MOOVIT / CITYMAPPER", "MOBILITY RECOVERY ENGINE"),
    ("Core Optimization Goal", "Shortest Path / Nominal Time", "Fixed Schedule Arrival", "Arrival Deadline Probability (OTP %)"),
    ("Traffic Uncertainty", "Static live traffic heatmaps", "Static scheduled timetable", "1,000-Run Monte Carlo Simulation"),
    ("Proactive Recovery", "None (Reroutes only post-jam)", "Shows next scheduled bus", "Dynamic Latest Safe Departure + Backup"),
    ("Diverse Alternatives", "1-2 minor road variations", "Timetable legs only", ">= 3 Guaranteed Distinct (<80% Overlap)"),
    ("Accidental Touch Guard", "None (Screen touch reroutes)", "None", "Route Lock with Confirmation Dialog"),
    ("Offline Autonomy", "Requires manual map download", "Requires active data plan", "Full PWA Service Worker + Local Cache"),
    ("API Licensing Cost", "Very expensive ($$$ per call)", "Proprietary paid licenses", "100% Free & Open-Source (Zero Paid APIs)")
]

top_t = 1.6
row_h = 0.58
for r_idx, r_data in enumerate(rows_data):
    y = top_t + r_idx * (row_h + 0.08)
    is_head = (r_idx == 0)
    bg_col = C_SURFACE_LIGHT if is_head else C_SURFACE
    bord_col = C_CYAN if is_head else C_BORDER
    
    # 4 column positions
    col_widths = [3.2, 2.7, 2.7, 3.133]
    cur_x = 0.8
    for c_idx, val in enumerate(r_data):
        w = col_widths[c_idx]
        is_winner = (c_idx == 3 and not is_head)
        cell_card = add_card(s14, cur_x, y, w, row_h, 
                             bg_color=RGBColor(26, 46, 53) if is_winner else bg_col, 
                             border_color=C_EMERALD if is_winner else bord_col)
        
        tb = s14.shapes.add_textbox(Inches(cur_x + 0.1), Inches(y + 0.08), Inches(w - 0.2), Inches(row_h - 0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(13 if not is_head else 14)
        p.font.bold = is_head or is_winner
        p.font.color.rgb = C_CYAN if is_head else (C_EMERALD if is_winner else C_TEXT_WHITE)
        
        cur_x += w + 0.06

# ==============================================================================
# SLIDE 15: Conclusion & Future Roadmap
# ==============================================================================
s15 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(s15)
add_header(s15, "Vision & Roadmap", "Never Late Again: The Future of Commute Reliability", 15)

add_card(s15, 0.8, 1.6, 5.7, 5.2, border_color=C_CYAN)
tb15_l = s15.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.8))
tf15_l = tb15_l.text_frame
tf15_l.word_wrap = True

p15_lh = tf15_l.paragraphs[0]
p15_lh.text = "KEY PROJECT TAKEAWAYS"
p15_lh.font.size = Pt(20)
p15_lh.font.bold = True
p15_lh.font.color.rgb = C_CYAN

takeaways = [
    ("Mathematical Arrival Certainty", "Pioneers deadline-driven routing replacing blind shortest-path navigation with empirical on-time probabilities."),
    ("Production-Ready Full-Stack System", "Built with modern FastAPI, React PWA, Leaflet, and SQLite, running 100% locally with zero paid API keys."),
    ("Commuter Stress Elimination", "Gives students and workers peace of mind with live Latest Safe Departure (LSD) countdowns and emergency contingency routes.")
]

for t_head, t_desc in takeaways:
    p_th = tf15_l.add_paragraph()
    p_th.text = f"• {t_head}:"
    p_th.font.size = Pt(15)
    p_th.font.bold = True
    p_th.font.color.rgb = C_EMERALD
    p_th.space_before = Pt(10)
    
    p_td = tf15_l.add_paragraph()
    p_td.text = f"  {t_desc}"
    p_td.font.size = Pt(14)
    p_td.font.color.rgb = C_TEXT_WHITE
    p_td.space_before = Pt(2)

# Right Side: Future Horizons
add_card(s15, 6.833, 1.6, 5.7, 5.2, border_color=C_AMBER)
tb15_r = s15.shapes.add_textbox(Inches(7.033), Inches(1.8), Inches(5.3), Inches(4.8))
tf15_r = tb15_r.text_frame
tf15_r.word_wrap = True

p15_rh = tf15_r.paragraphs[0]
p15_rh.text = "FUTURE HORIZONS & ROADMAP"
p15_rh.font.size = Pt(20)
p15_rh.font.bold = True
p15_rh.font.color.rgb = C_AMBER

horizons = [
    ("Real-Time Crowdsourced Bus Beacons", "Integrate low-cost Bluetooth/GPS telemetry from commuter phones to track live government bus positions."),
    ("Monsoon & Weather Impact Modeling", "Incorporate live precipitation radar data to predict waterlogging speed penalties across Indian state highways."),
    ("Dynamic Rideshare Split Recovery", "Automatically summon auto-rickshaws or cabs to bridge connection gaps whenever a primary bus is delayed.")
]

for h_head, h_desc in horizons:
    p_hh = tf15_r.add_paragraph()
    p_hh.text = f"• {h_head}:"
    p_hh.font.size = Pt(15)
    p_hh.font.bold = True
    p_hh.font.color.rgb = C_CYAN
    p_hh.space_before = Pt(10)
    
    p_hd = tf15_r.add_paragraph()
    p_hd.text = f"  {h_desc}"
    p_hd.font.size = Pt(14)
    p_hd.font.color.rgb = C_TEXT_WHITE
    p_hd.space_before = Pt(2)

# Save presentation
output_path = r"d:\LSM PROJECT\Mobility_Recovery_Engine_Presentation.pptx"
prs.save(output_path)
print(f"SUCCESS: Presentation successfully generated at: {output_path}")
