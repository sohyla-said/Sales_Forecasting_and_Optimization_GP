import streamlit as st
import pandas as pd

@st.cache_data
def load_date():
    data = pd.read_csv('processed_data.csv')
    return data
data = load_date()

st.title("📊 Interactive Dashboard for Sales Forecasting Data Analysis")