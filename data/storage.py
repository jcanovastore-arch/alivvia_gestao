# data/storage.py
import streamlit as st

def save_dataframe(name, df):
    st.session_state[name] = df

def load_dataframe(name):
    return st.session_state.get(name)
