/* =========================================================
   ACCESSIBILITY — WCAG-ORIENTED UI IMPROVEMENTS
   ========================================================= */

/* Keyboard navigation: highly visible focus indicator */
*:focus-visible {
    outline: 3px solid #00F0FF !important;
    outline-offset: 3px !important;
    border-radius: 4px !important;
}

/* Minimum comfortable interactive target */
.stButton > button,
.stDownloadButton > button {
    min-height: 44px !important;
    min-width: 44px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* Form controls */
input,
textarea,
select,
[data-baseweb="select"],
[data-baseweb="input"] {
    min-height: 44px !important;
    font-size: 16px !important;
}

/* Accessible form labels */
label,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stMultiSelect label,
.stRadio label,
.stCheckbox label,
.stSlider label {
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.4 !important;
}

/* Readable body content */
p,
li,
.stMarkdown,
.stCaption {
    line-height: 1.6 !important;
}

/* Never depend on color alone for important controls */
.stButton > button {
    border-width: 2px !important;
}

/* Strong text contrast */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    line-height: 1.5 !important;
}

/* Comfortable headings */
h1,
h2,
h3,
h4 {
    line-height: 1.3 !important;
}

/* Avoid tiny interface text */
small,
.stCaption {
    font-size: 14px !important;
}

/* Better spacing for keyboard/touch interaction */
.stButton {
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}

/* Respect users who prefer reduced motion */
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

/* Prevent horizontal overflow on small screens */
.block-container {
    overflow-wrap: anywhere;
}

/* Preserve readable text inside custom NEXUS cards */
.spec-val,
.flow-step-val,
.brand-tagline {
    overflow-wrap: anywhere;
    word-break: normal;
}
