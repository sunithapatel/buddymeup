"""
streamlit run app.py
helpful resources:
https://www.youtube.com/watch?v=6acv9LL6gHg&list=PLJ39kWiJXSixyRMcn3lrbv8xI8ZZoYNZU&index=2
https://github.com/MarcSkovMadsen/awesome-streamlit/blob/master/app.py
"""

import streamlit as st
from app_pages import make_pages

st.set_page_config(page_title="BuddyMeUp", page_icon="assets/images/icon_buddymeup.png")

def main():
    make_pages()

if __name__ == "__main__":
    main()