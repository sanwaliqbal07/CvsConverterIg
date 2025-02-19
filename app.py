import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Setting up the App
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("🧹 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualizations.")

# Advanced Custom CSS for better UI

def set_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            color: #ffffff;
            font-family: Arial, sans-serif;
            padding: 20px;
            border-radius: 10px;
        }
        .block-container {
            max-width: 1200px;
        }
        .stButton>button {
            background-color: #6a11cb;
            color: white;
            border-radius: 10px;
            padding: 10px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #2575fc;
        }
        .stDataFrame {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 10px;
        }
        .stRadio label {
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
set_custom_css()

# File uploader
uploaded_files = st.file_uploader("Upload Your File (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue
        
        # Display file details
        st.subheader(f"📕 File: {file.name}")
        st.write(f"**📐 Size:** {round(file.size / 1024, 2)} KB")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("🧹 Data Cleaning Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Remove Duplicates from {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates Removed!")
        
        with col2:
            fill_method = st.selectbox("Fill Missing Values Method:", ["Mean", "Median", "Mode"], key=file.name)
            if st.button(f"Fill Missing Values for {file.name}"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                if fill_method == "Mean":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                elif fill_method == "Median":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                elif fill_method == "Mode":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mode().iloc[0])
                st.success("Missing Values Filled!")
        
        # Column selection
        st.subheader("🔀 Select Columns to Keep")
        selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]
        
  # Visualization
        st.subheader("📉📈 Data Visualization")
        numeric_columns = df.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            chart_type = st.selectbox("Choose Chart Type", ["Bar Chart", "Line Chart"], key=f"chart_{file.name}")
            col_to_plot = st.selectbox("Choose a Column to Visualize", numeric_columns, key=f"col_{file.name}")
            
            if chart_type == "Bar Chart":
                st.bar_chart(df[col_to_plot])
            else:
                st.line_chart(df[col_to_plot])
        else:
            st.warning("No numeric columns available for visualization.")
        
        # Conversion options
        st.subheader("🔀 File Conversion")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("✅ All files processed successfully!")