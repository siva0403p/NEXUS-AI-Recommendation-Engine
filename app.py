"""
NEXUS - Intelligent AI Short-Form Recommendation Assistant
End-to-End Dynamic Recommendation Agent & Interactive Feedback Loop
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Page Configuration
st.set_page_config(
    page_title="NEXUS | From Scroll to Skill",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern & Accessible CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
    max-width: 1000px;
}

/* Accessibility improvements */
*:focus-visible {
    outline: 3px solid #00F0FF !important;
    outline-offset: 3px !important;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 44px !important;
    min-width: 44px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

input,
textarea,
select {
    min-height: 44px !important;
    font-size: 16px !important;
}

label {
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.4 !important;
}

p,
li {
    line-height: 1.6 !important;
}

h1,
h2,
h3,
h4 {
    line-height: 1.3 !important;
}

.stCaption {
    font-size: 14px !important;
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}

/* Header */
.app-header {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 14, 26, 0.95) 100%);
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 14px;
    padding: 18px 24px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.brand-title {
    font-size: 1.9rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00F0FF 0%, #38BDF8 50%, #A855F7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.brand-tagline {
    color: #94A3B8;
    font-size: 0.92rem;
    font-weight: 500;
    margin-top: 2px;
}

.demo-mode-pill {
    background: rgba(0, 240, 255, 0.1);
    border: 1px solid rgba(0, 240, 255, 0.3);
    color: #00F0FF;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Flow Step Card */
.flow-step-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.flow-step-label {
    font-size: 0.72rem;
    font-weight: 800;
    color: #00F0FF;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.flow-step-val {
    font-size: 0.88rem;
    font-weight: 700;
    color: #FFFFFF;
    white-space: normal;
    overflow-wrap: anywhere;
}

/* Spec Item */
.spec-box {
    background: #080C18;
    border: 2px solid #00F0FF;
    border-radius: 14px;
    padding: 22px 26px;
    margin-top: 14px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 240, 255, 0.12);
}

.spec-line {
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    white-space: normal;
    overflow-wrap: anywhere;
}

.spec-line:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.spec-key {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 800;
    color: #00F0FF;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 2px;
}

.spec-val {
    color: #F8FAFC;
    font-size: 1.0rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# Imports from existing working backend packages (FROZEN)
from config import (
    WEIGHT_SEMANTIC_RELEVANCE,
    WEIGHT_INTEREST_ALIGNMENT,
    WEIGHT_NOVELTY,
    WEIGHT_EDUCATIONAL_VALUE,
    WEIGHT_DIFFICULTY_FIT,
    HYPE_SUPPRESSION_THRESHOLD
)
from services.data_loader import DataLoader
from engine.nexus_pipeline import NexusPipeline
from models.schemas import ReelItem, RecommendationOutput

# Load Data and Pipeline
@st.cache_resource
def get_data_loader():
    return DataLoader()

data_loader = get_data_loader()
presets = data_loader.get_test_presets()

# Sidebar: Controls & Presets
with st.sidebar:
    st.markdown("### ⚡ **NEXUS ASSISTANT**")
    st.caption("Adaptive Technology Recommendation Agent")
    st.divider()

    # 1. API Configuration
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Optional: Enter Gemini API key for live Google GenAI LLM structured reasoning. If empty, the verified local semantic engine is active."
    )
    
    if api_key_input:
        st.success("🟢 Gemini 2.5 Flash: Active", icon="✅")
    else:
        st.info("🔵 Semantic Engine: Active", icon="⚡")

    st.divider()

    # 2. Presets / Stream Selector
    st.markdown("#### 🎯 **Select Scenario Stream**")
    preset_names = list(presets.keys())
    selected_preset_name = st.selectbox(
        "Load Interaction Stream:",
        preset_names,
        index=0,
        help="Default History contains the 8 watched reels."
    )

    if st.button("🔄 Load Selected Stream", use_container_width=True):
        st.session_state["history_reels"] = list(presets.get(selected_preset_name, data_loader.interaction_history))
        st.session_state["selected_reel_idx"] = 0
        st.session_state["trail"] = []
        st.session_state["recommendation_output"] = None
        st.session_state["feedback_given"] = False
        st.session_state["interaction_map"] = {i: "Watched fully" for i in range(len(st.session_state["history_reels"]))}
        st.rerun()

    st.divider()
    st.caption("NEXUS v2.0 • Hackathon Edition")

# Initialize Pipeline with active API key
if "pipeline" not in st.session_state or st.session_state.get("current_api_key") != api_key_input:
    st.session_state["pipeline"] = NexusPipeline(api_key=api_key_input)
    st.session_state["current_api_key"] = api_key_input

pipeline: NexusPipeline = st.session_state["pipeline"]

# Initialize Session State
if "history_reels" not in st.session_state:
    st.session_state["history_reels"] = list(presets.get(selected_preset_name, data_loader.interaction_history))
if "selected_reel_idx" not in st.session_state:
    st.session_state["selected_reel_idx"] = 0
if "trail" not in st.session_state:
    st.session_state["trail"] = ["Java", "Software Engineering"]
if "recommendation_output" not in st.session_state:
    st.session_state["recommendation_output"] = None
if "feedback_given" not in st.session_state:
    st.session_state["feedback_given"] = False
if "interaction_map" not in st.session_state:
    st.session_state["interaction_map"] = {i: "Watched fully" for i in range(len(st.session_state["history_reels"]))}

# Ensure index bounds
active_history: list[ReelItem] = st.session_state["history_reels"]
if not active_history:
    active_history = list(data_loader.interaction_history)
    st.session_state["history_reels"] = active_history

sel_idx = min(st.session_state["selected_reel_idx"], len(active_history) - 1)
current_reel = active_history[sel_idx]

# ==============================================================================
# HEADER
# ==============================================================================
source_mode = "LIVE AI ANALYSIS — GEMINI GENAI ENGINE" if pipeline.gemini_service.is_available() else "DEMO MODE — FICTIONAL REEL CORPUS"

st.markdown(f"""<div class="app-header">
    <div>
        <h1 class="brand-title">⚡ NEXUS</h1>
        <div class="brand-tagline">"From what you scroll to what you should discover next."</div>
        <div style="color: #64748B; font-size: 0.85rem; margin-top: 2px;">
            An AI agent that infers the hidden technology interests behind your scrolling and finds the next useful thing to learn.
        </div>
    </div>
    <div style="text-align: right;">
        <span class="demo-mode-pill">{source_mode}</span>
    </div>
</div>""", unsafe_allow_html=True)

# ==============================================================================
# 1. WHAT THE STUDENT INTERACTED WITH (ALL REELS IN THE INTERACTION STREAM)
# ==============================================================================
st.markdown("### 🎬 **Student Interaction Stream**")
st.caption("NEXUS analyzes the entire interaction sequence to detect patterns across topics and context — not a single keyword.")

with st.container(border=True):
    st.markdown(f"**Stream Contents ({len(active_history)} Reels Analyzed):**")
    
    # Render all reels in the active interaction stream
    cols_per_row = 4
    num_rows = (len(active_history) + cols_per_row - 1) // cols_per_row
    
    for r_idx in range(num_rows):
        cols = st.columns(cols_per_row)
        for c_idx in range(cols_per_row):
            item_idx = r_idx * cols_per_row + c_idx
            if item_idx < len(active_history):
                r = active_history[item_idx]
                state_label = st.session_state["interaction_map"].get(item_idx, "Watched fully")
                is_selected = (item_idx == sel_idx)
                
                with cols[c_idx]:
                    border_color = "#00F0FF" if is_selected else "rgba(255,255,255,0.1)"
                    st.markdown(f"""<div style="border: 1px solid {border_color}; background: rgba(15,23,42,0.8); border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                        <div style="font-size: 0.72rem; color: #00F0FF; font-weight: 800;">REEL #{item_idx + 1} • {r.category.upper()}</div>
                        <div style="font-weight: 700; font-size: 0.88rem; color: #FFFFFF; margin: 4px 0;">"{r.title}"</div>
                        <div style="font-size: 0.75rem; color: #94A3B8;"><b>State:</b> <span style="color: #34D399;">{state_label}</span></div>
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    # Interactive Reel Selector & Signal Customizer
    st.markdown(f"#### ✏️ **Customize Interaction for Reel #{sel_idx + 1}: \"{current_reel.title}\"**")
    
    col_sel, col_act = st.columns([1, 2])
    with col_sel:
        new_sel_idx = st.selectbox(
            "Select Reel to Edit:",
            range(len(active_history)),
            format_func=lambda i: f"#{i+1}: {active_history[i].title} ({active_history[i].category})",
            index=sel_idx
        )
        if new_sel_idx != sel_idx:
            st.session_state["selected_reel_idx"] = new_sel_idx
            st.rerun()

    with col_act:
        user_interaction = st.radio(
            "Your Interaction:",
            ["❤️ Loved it", "👀 Watched fully", "🔁 Rewatched", "💾 Saved", "↗ Shared", "⏭ Skipped"],
            index=0,
            horizontal=True
        )
        st.session_state["interaction_map"][sel_idx] = user_interaction

    col_chips, col_note = st.columns([1, 1])
    with col_chips:
        user_chips = st.multiselect(
            "What caught your attention?",
            ["Problem Solving", "Software Engineering", "Developer Culture", "Architecture", "Backend Systems", "Career Growth", "Python & Data", "AI & Tools"],
            default=["Software Engineering", "Problem Solving"]
        )

    with col_note:
        user_note = st.text_input(
            "Tell NEXUS what interested you (optional):",
            placeholder="e.g. I liked the developer problem-solving part and want to understand real scale",
            value=""
        )

    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        btn_find = st.button("🧠 FIND MY NEXT DISCOVERY", type="primary", use_container_width=True)

# ==============================================================================
# 2. RUN PIPELINE DYNAMICALLY
# ==============================================================================
if btn_find or st.session_state["recommendation_output"] is None:
    with st.spinner("NEXUS is inferring your latent interest & connecting next-skill dots..."):
        augmented_history = [r for r in active_history]
        
        custom_signals = []
        if user_chips:
            custom_signals.extend([c.lower().replace(" ", "-") for c in user_chips])
        if user_note:
            custom_signals.append(user_note.strip().lower())
        
        if custom_signals:
            signal_str = ",".join(custom_signals)
            augmented_history[sel_idx] = ReelItem(
                reel_id=current_reel.reel_id,
                title=current_reel.title,
                category=current_reel.category,
                topic=current_reel.topic,
                difficulty=current_reel.difficulty,
                educational_value=current_reel.educational_value,
                hype_score=current_reel.hype_score,
                semantic_tags=f"{current_reel.semantic_tags},{signal_str}",
                prerequisites=current_reel.prerequisites
            )
        
        output, latent_interest, next_skill, analyses = pipeline.run(augmented_history)
        st.session_state["recommendation_output"] = output
        st.session_state["latent_interest"] = latent_interest
        st.session_state["next_skill"] = next_skill
        st.session_state["feedback_given"] = False

output: RecommendationOutput = st.session_state["recommendation_output"]
latent_interest = st.session_state.get("latent_interest")
next_skill = st.session_state.get("next_skill")

# ==============================================================================
# 3. WHAT NEXUS UNDERSTOOD (REASONING & SEMANTIC FLOW)
# ==============================================================================
if output:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 **What NEXUS Understood**")
    
    with st.container(border=True):
        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            st.markdown(f"#### Latent Interest: <span style='color: #00F0FF;'>{output.interest_detected}</span>", unsafe_allow_html=True)
            st.markdown(f"**WHY?**\n\n{output.why_evidence}")
        with col_u2:
            st.markdown(f"**Confidence Level:**\n\n<span style='color: #34D399; font-weight: 800; font-size: 1.1rem;'>{output.confidence}</span>", unsafe_allow_html=True)
            st.markdown(f"**Next Target Skill:**\n\n<span style='color: #38BDF8; font-weight: 800; font-size: 1.05rem;'>{next_skill.next_skill}</span>", unsafe_allow_html=True)

    # 4. READABLE SEMANTIC FLOW PATH (Clean connected flow cards without label overlap)
    st.markdown("### 🔗 **Semantic Flow Path**")
    st.caption("How NEXUS moves from surface signals to latent interest to the next tech discovery:")
    
    flow_col1, flow_col2, flow_col3, flow_col4, flow_col5 = st.columns(5)
    
    surface_summary = ", ".join(list(set(r.category for r in active_history))[:3])
    semantic_summary = ", ".join(list(latent_interest.semantic_clusters.keys())[:2]) or "Engineering Context"
    
    with flow_col1:
        st.markdown(f"""<div class="flow-step-card">
            <div class="flow-step-label">1. Surface Signals</div>
            <div class="flow-step-val">{surface_summary}</div>
        </div>""", unsafe_allow_html=True)
    
    with flow_col2:
        st.markdown(f"""<div class="flow-step-card">
            <div class="flow-step-label">2. Semantic Clusters</div>
            <div class="flow-step-val">{semantic_summary}</div>
        </div>""", unsafe_allow_html=True)

    with flow_col3:
        st.markdown(f"""<div class="flow-step-card" style="border-color: #00F0FF; background: rgba(0,240,255,0.08);">
            <div class="flow-step-label" style="color: #00F0FF;">3. Latent Interest</div>
            <div class="flow-step-val" style="color: #00F0FF;">{output.interest_detected}</div>
        </div>""", unsafe_allow_html=True)

    with flow_col4:
        st.markdown(f"""<div class="flow-step-card">
            <div class="flow-step-label">4. Next Skill</div>
            <div class="flow-step-val" style="color: #38BDF8;">{next_skill.next_skill}</div>
        </div>""", unsafe_allow_html=True)

    with flow_col5:
        st.markdown(f"""<div class="flow-step-card" style="border-color: #10B981; background: rgba(16,185,129,0.08);">
            <div class="flow-step-label" style="color: #10B981;">5. Discovery</div>
            <div class="flow-step-val" style="color: #34D399;">{output.recommended_tech_reel.title}</div>
        </div>""", unsafe_allow_html=True)

    # ==============================================================================
    # 5. YOUR NEXT TECH DISCOVERY (PRIMARY REQUIRED OUTPUT CARD)
    # ==============================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🌟 **YOUR NEXT TECH DISCOVERY**")
    st.caption("Official competition output generated dynamically from the active pipeline result:")

    rec = output.recommended_tech_reel
    st.markdown(f"""<div class="spec-box">
        <div class="spec-line">
            <span class="spec-key">CURRENT REEL:</span>
            <span class="spec-val">{output.current_reel_reference}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">INTEREST DETECTED:</span>
            <span class="spec-val" style="color: #00F0FF; font-weight: 800; font-size: 1.15rem;">{output.interest_detected}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">WHY:</span>
            <span class="spec-val">{output.why_evidence}</span>
        </div>
        <div class="spec-line" style="background: rgba(0, 240, 255, 0.08); padding: 12px 14px; border-radius: 8px; border-left: 3px solid #00F0FF;">
            <span class="spec-key" style="color: #FFFFFF;">RECOMMENDED TECH REEL:</span>
            <span class="spec-val" style="color: #FFFFFF; font-weight: 900; font-size: 1.25rem;">🌟 "{rec.title}"</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">CATEGORY:</span>
            <span class="spec-val">{output.category}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">WHY THIS RECOMMENDATION:</span>
            <span class="spec-val">{output.why_this_recommendation}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">DIFFICULTY:</span>
            <span class="spec-val" style="font-weight: 700; color: #F8FAFC;">{output.difficulty}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">CONFIDENCE:</span>
            <span class="spec-val" style="color: #34D399; font-weight: 800;">{output.confidence}</span>
        </div>
        <div class="spec-line">
            <span class="spec-key">NEXUS SCORE:</span>
            <span class="spec-val" style="color: #00F0FF; font-weight: 800;">{output.nexus_score}/100</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Supporting Evidence Metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"**NEXUS Score:** `{output.nexus_score}/100`")
    with col_m2:
        st.markdown(f"**Educational Value:** `{int(rec.educational_value * 100)}%`")
    with col_m3:
        st.markdown(f"**Hype Score:** `{int(rec.hype_score * 100)}%`")
    with col_m4:
        st.markdown(f"**Target Skill:** `{next_skill.next_skill}`")

    # ==============================================================================
    # 6. WHY NOT THIS VIRAL REEL? (QUALITY GATE HYPE SUPPRESSION)
    # ==============================================================================
    if output.rejected_candidate:
        rej = output.rejected_candidate.reel
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 🛑 **WHY NOT THE VIRAL REEL?** &nbsp; <span style='color: #EF4444; font-size: 0.8rem;'>(SUPPRESSED BY QUALITY GATE)</span>", unsafe_allow_html=True)
            st.error(f"**Suppressed Candidate:** \"{rej.title}\"\n\n"
                     f"• **Hype Score:** {int(rej.hype_score*100)}% &nbsp;|&nbsp; **Educational Value:** {int(rej.educational_value*100)}%\n\n"
                     f"• **Rejection Reason:** {output.why_not_this or 'Suppressed due to high clickbait hype and low educational substance despite keyword overlap.'}")

    # ==============================================================================
    # 7. WAS THIS RECOMMENDATION USEFUL? (ACTIVE FEEDBACK LOOP)
    # ==============================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### **Was this recommendation useful?**")
        
        col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 2])
        with col_fb1:
            if st.button("👍 Yes, this is relevant", use_container_width=True):
                st.session_state["feedback_type"] = "yes"
                st.session_state["feedback_given"] = True
        with col_fb2:
            if st.button("👎 No, find another", use_container_width=True):
                st.session_state["feedback_type"] = "no"
                st.session_state["feedback_given"] = True

        if st.session_state.get("feedback_given"):
            if st.session_state.get("feedback_type") == "yes":
                st.success("✅ **Great! NEXUS logged your preference.** Next recommendations will continue advancing this skill path.")
                if st.button("⏭️ ACCEPT & ADVANCE TO NEXT REEL", type="primary"):
                    st.session_state["history_reels"].append(rec)
                    st.session_state["selected_reel_idx"] = len(st.session_state["history_reels"]) - 1
                    st.session_state["interaction_map"][st.session_state["selected_reel_idx"]] = "Saved"
                    if rec.category not in st.session_state["trail"]:
                        st.session_state["trail"].append(rec.category)
                    st.session_state["recommendation_output"] = None
                    st.session_state["feedback_given"] = False
                    st.rerun()

            elif st.session_state.get("feedback_type") == "no":
                st.markdown("**Why didn't you like it?**")
                refine_reason = st.selectbox(
                    "Feedback reason:",
                    ["Too advanced", "Not interesting", "Wrong topic", "Too generic", "I wanted something practical", "Other"],
                    label_visibility="collapsed"
                )
                if st.button("🔄 FIND A BETTER ONE", type="primary"):
                    with st.spinner("Adjusting weights based on feedback & re-ranking..."):
                        if refine_reason == "Too advanced":
                            pipeline.ranking_engine.w_dif = 0.35
                        elif refine_reason == "I wanted something practical":
                            pipeline.ranking_engine.w_edu = 0.30
                        
                        filtered_candidates = [c for c in data_loader.candidate_reels if c.reel_id != rec.reel_id]
                        output_new, lat_new, nxt_new, _ = pipeline.run(
                            active_history,
                            candidates=filtered_candidates
                        )
                        st.session_state["recommendation_output"] = output_new
                        st.session_state["feedback_given"] = False
                        st.rerun()

    # ==============================================================================
    # 8. LEARNING TRAIL
    # ==============================================================================
    trail_items = st.session_state.get("trail", ["Java", "Software Engineering", "System Design"])
    if next_skill and next_skill.target_category not in trail_items:
        trail_items.append(next_skill.target_category)

    trail_str = " ➔ ".join([f"`{item}`" for item in trail_items[:6]])
    st.markdown(f"**🌱 LEARNING TRAIL:** &nbsp; {trail_str}")

    # ==============================================================================
    # 9. TECHNICAL DIAGNOSTICS (EXPANDER)
    # ==============================================================================
    with st.expander("🔬 Technical Diagnostics & Scoring Breakdown", expanded=False):
        st.markdown(r"""$$\text{NEXUS Score} = 0.35 \cdot S_{rel} + 0.25 \cdot S_{int} + 0.15 \cdot S_{nov} + 0.15 \cdot S_{edu} + 0.10 \cdot S_{dif} - P_{hype} - P_{red}$$""")
        st.json(output.score_breakdown)
        st.json({
            "latent_interest": latent_interest.model_dump(),
            "next_skill": next_skill.model_dump()
        })
