import streamlit as st
from scipy import stats
import numpy as np
import pandas as pd
import io

st.title("Clinical Trial Effect Size Analyzer")
st.markdown("""
This tool calculates **t-value**, **p-value**, and **Cohen's d** from group statistics
(mean, SD, and N), and provides an interpretation of potential significance.
It also projects future trends assuming linear growth. Program belongs to VALENSA INTERNATIONAL
""")

st.header("📥 Input Parameters")

parameter_name = st.text_input("Name of clinical parameter", value="Anterior Terminal Hair Count")

n_active = st.number_input("Sample size: Active group (n1)", min_value=2, value=20)
mean_active = st.number_input("Mean change: Active group at Day 90", value=11.0)
sd_active = st.number_input("Standard deviation: Active group", value=18.28)
baseline_active = st.number_input("Baseline value: Active group", value=121.4)

n_placebo = st.number_input("Sample size: Placebo group (n2)", min_value=2, value=10)
mean_placebo = st.number_input("Mean change: Placebo group at Day 90", value=1.9)
sd_placebo = st.number_input("Standard deviation: Placebo group", value=16.22)
baseline_placebo = st.number_input("Baseline value: Placebo group", value=124.2)

project_to_day = st.number_input("Project data to how many total days?", min_value=90, value=180, step=30)
current_day = 90

file_name = st.text_input("Enter filename for Excel download (without extension)", value="trial_results")

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

    # Step 8: Projection assuming linear growth
    growth_factor = project_to_day / current_day
    projected_active = mean_active * growth_factor
    projected_placebo = mean_placebo * growth_factor
    projected_diff = projected_active - projected_placebo
    projected_d = projected_diff / sp

    if projected_d < 0.2:
        proj_interpretation = "Projected effect likely to remain minimal."
    elif projected_d < 0.5:
        proj_interpretation = "Projected effect may still be borderline."
    elif projected_d < 0.8:
        proj_interpretation = "Projected effect likely to reach moderate significance."
    else:
        proj_interpretation = "Projected effect likely to reach strong significance."

    # Step 9: Calculate % change from baseline
    pct_change_active = (mean_active / baseline_active) * 100
    pct_change_placebo = (mean_placebo / baseline_placebo) * 100

    st.header("📊 Results")
    st.write(f"**Parameter:** {parameter_name}")
    st.write(f"**Mean Difference (Day 90):** {mean_diff:.2f} units")
    st.write(f"**Pooled Standard Deviation:** {sp:.2f}")
    st.write(f"**t-value:** {t_value:.2f}")
    st.write(f"**p-value (two-tailed):** {p_value:.3f}")
    st.write(f"**Cohen's d (Effect Size):** {cohen_d:.2f}")
    st.write(f"**% Change from Baseline (Active):** {pct_change_active:.2f}%")
    st.write(f"**% Change from Baseline (Placebo):** {pct_change_placebo:.2f}%")
    st.success(interpretation)

    st.header("📈 Projection to Day " + str(project_to_day))
    st.write(f"**Projected Mean Change (Active):** {projected_active:.2f}")
    st.write(f"**Projected Mean Change (Placebo):** {projected_placebo:.2f}")
    st.write(f"**Projected Mean Difference:** {projected_diff:.2f}")
    st.write(f"**Projected Cohen's d:** {projected_d:.2f}")
    st.success(proj_interpretation)

    # Prepare DataFrame
    df_output = pd.DataFrame({
        "Parameter": [parameter_name],
        "Day 90 Mean Difference": [mean_diff],
        "Pooled SD": [sp],
        "t-value": [t_value],
        "p-value": [p_value],
        "Cohen's d": [cohen_d],
        "% Change Active": [pct_change_active],
        "% Change Placebo": [pct_change_placebo],
        f"Projected Mean Difference (Day {project_to_day})": [projected_diff],
        f"Projected Cohen's d (Day {project_to_day})": [projected_d],
        "Interpretation": [interpretation],
        "Projected Interpretation": [proj_interpretation]
    })

    # Export to Excel using BytesIO
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_output.to_excel(writer, index=False)
    output.seek(0)

    st.download_button("📥 Download Results as Excel, COPYRIGHT A.PANDE@VALENSA.COM", data=output, file_name=f"{file_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
