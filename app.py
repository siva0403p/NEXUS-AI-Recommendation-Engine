# Accessibility improvements

import streamlit as st
import pandas as pd
import numpy as np
st.markdown("""
<style>

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

</style>
""", unsafe_allow_html=True)
