import streamlit as st
from scipy import stats
import numpy as np

st.title("Clinical Trial Effect Size Analyzer")
st.markdown("""
This tool calculates **t-value**, **p-value**, and **Cohen's d** from group statistics
(mean, SD, and N), and provides an interpretation of potential significance.
""")

st.header("📥 Input Parameters")

n_active = st.number_input("Sample size: Active group (n1)", min_value=2, value=20)
mean_active = st.number_input("Mean change: Active group", value=11.0)
sd_active = st.number_input("Standard deviation: Active group", value=18.28)

n_placebo = st.number_input("Sample size: Placebo group (n2)", min_value=2, value=10)
mean_placebo = st.number_input("Mean change: Placebo group", value=1.9)
sd_placebo = st.number_input("Standard deviation: Placebo group", value=16.22)

if st.button("Calculate"):
    # Step 1: Mean difference
    mean_diff = mean_active - mean_placebo

    # Step 2: Pooled SD
    sp_squared = ((n_active - 1) * sd_active**2 + (n_placebo - 1) * sd_placebo**2) / (n_active + n_placebo - 2)
    sp = np.sqrt(sp_squared)

    # Step 3: t-value
    t_value = mean_diff / (sp * np.sqrt(1/n_active + 1/n_placebo))

    # Step 4: Degrees of freedom
    df = n_active + n_placebo - 2

    # Step 5: Two-tailed p-value
    p_value = stats.t.sf(np.abs(t_value), df) * 2

    # Step 6: Cohen's d
    cohen_d = mean_diff / sp

    # Step 7: Interpretation
    if cohen_d < 0.2:
        interpretation = "Very small effect – unlikely to be clinically meaningful."
    elif cohen_d < 0.5:
        interpretation = "Small effect – borderline meaningful, may need more data or time."
    elif cohen_d < 0.8:
        interpretation = "Moderate effect – likely to become significant with more time or sample size."
    else:
        interpretation = "Large effect – highly likely to become statistically and clinically significant."

    st.header("📊 Results")
    st.write(f"**Mean Difference:** {mean_diff:.2f} hairs")
    st.write(f"**Pooled Standard Deviation:** {sp:.2f}")
    st.write(f"**t-value:** {t_value:.2f}")
    st.write(f"**p-value (two-tailed):** {p_value:.3f}")
    st.write(f"**Cohen's d (Effect Size):** {cohen_d:.2f}")
    st.success(interpretation)
