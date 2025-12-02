# data/cache.py
import streamlit as st

@st.cache_data
def get_cache(key):
    return st.session_state.get(key)

@st.cache_data
def set_cache(key, value):
    st.session_state[key] = value
