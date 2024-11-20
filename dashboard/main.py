import pandas as pd
import streamlit as st
import streamlit_shadcn_ui as ui
from func import calculate_metrics
from visualization import create_pie_chart, create_funnel_chart, create_plot_average_by_group, create_treemap

# Load the data
try:
    df = pd.read_csv(r'D:\belajar program\Sleep health and lifestyle dataset\data\sleep_health.csv')
except FileNotFoundError:
    st.error("File 'data/sleep_health.csv' tidak ditemukan. Pastikan file tersebut berada di folder 'data'.")
    st.stop()

# Set the page layout to wide
st.set_page_config(layout="wide")

# Sidebar for filtering based on sleep disorders
if "sleep_disorder" in df.columns:
    sleep_disorder = df["sleep_disorder"].unique().tolist()
    with st.sidebar:
        st.text("Total Population:")
        ui.badges(badge_list=[(f"{len(df)}", "secondary")], key="total_data")
        selected_data = st.multiselect("Select Data Based on Sleep Disorder", sleep_disorder, sleep_disorder)

    # Filter the dataframe based on the selected sleep disorders
    filtered_df = df[df["sleep_disorder"].isin(selected_data)] if selected_data else df
else:
    st.error("Kolom 'sleep_disorder' tidak ditemukan dalam dataset.")
    filtered_df = df  # Fallback jika kolom tidak ditemukan.

# Prepare filtered dataframe for visuals
gender_icons = {
    'Female': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Venus_symbol.svg/120px-Venus_symbol.svg.png',
    'Male': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Mars_symbol.svg/120px-Mars_symbol.svg.png'
}
df_visual = filtered_df.copy()
df_visual["gender"] = df_visual["gender"].map(gender_icons)
df_visual["sleep_disorder"] = df_visual["sleep_disorder"].apply(lambda x: True if x != "No Issue" else False)
df_visual.drop(["age_group"], axis=1, inplace=True, errors='ignore')  # Jangan hapus blood_pressure_category

# Get the metrics
try:
    metrics = calculate_metrics(filtered_df)
except Exception as e:
    st.error(f"Error saat menghitung metrik: {e}")
    metrics = []

# Display the metrics dynamically
cols = st.columns(len(metrics)) if metrics else st.columns(1)
for i, metric in enumerate(metrics):
    with cols[i]:
        ui.metric_card(
            title=metric["title"],
            content=metric["content"],
            description=metric["trend"],
            key=f"metric-{i+1}"
        )

# Display first visual column
first_visual = st.columns(3)
try:
    # Pie chart untuk gender
    if "gender" in df_visual.columns:
        first_visual[0].plotly_chart(create_pie_chart(df_visual, "gender", "Gender", hole=0.4))
    else:
        st.error("Kolom 'gender' tidak ditemukan dalam dataset visual.")

    # Funnel chart untuk blood_pressure_category
    if "blood_pressure_category" in df_visual.columns:
        first_visual[1].plotly_chart(create_funnel_chart(df_visual, column="blood_pressure_category", label="Blood Pressure"))
    else:
        st.error("Kolom 'blood_pressure_category' tidak ditemukan dalam dataset visual.")

    # Pie chart untuk BMI
    if "bmi_category" in df_visual.columns:
        first_visual[2].plotly_chart(create_pie_chart(df_visual, "bmi_category", "BMI"))
    else:
        st.error("Kolom 'bmi_category' tidak ditemukan dalam dataset visual.")
except Exception as e:
    st.error(f"Error saat menampilkan visualisasi: {e}")

# Display second visual column
second_visual = st.columns(2)
try:
    # Menampilkan Treemap di second_visual[0]
    second_visual[0].plotly_chart(create_treemap(df_visual, column="bmi_category", label="BMI Category"))

    # Menampilkan DataFrame di second_visual[1]
    with second_visual[1]:
        st.markdown("**DataFrame Version**")
        st.dataframe(df_visual, column_config={
            "gender": st.column_config.ImageColumn(),
            "sleep_disorder": st.column_config.CheckboxColumn(disabled=True),
            "quality_of_sleep": st.column_config.ProgressColumn(
                format="%f",
                min_value=0,
                max_value=10,
            ),
            "stress_level": st.column_config.ProgressColumn(
                format="%f",
                min_value=0,
                max_value=10,
            ),
        }, hide_index=True)
except Exception as e:
    st.error(f"Error saat menampilkan visualisasi kedua: {e}")


# Display third visual column
third_visual = st.columns(2)
try:
    third_visual[0].plotly_chart(create_plot_average_by_group(df, group_column="age_group", value_column="daily_steps"))
    third_visual[1].plotly_chart(create_plot_average_by_group(df, group_column="age_group", value_column="sleep_duration"))
except Exception as e:
    st.error(f"Error saat menampilkan visualisasi ketiga: {e}")
