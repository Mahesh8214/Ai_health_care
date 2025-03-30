import streamlit as st
from data_pipeline.data_models import ResearchContext

def setup_page_config():
    st.set_page_config(
        page_title="Professional Research Agent",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def display_response(text: str, is_followup: bool = False):
    """Display response with appropriate formatting"""
    if is_followup:
        st.markdown(f"""
        <div style='background-color:#2d3748; color:white; padding:1rem; border-radius:8px; margin-bottom:1rem; border-left:4px solid #4a5568;'>
            {text}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='font-family:Arial,sans-serif; line-height:1.6;'>
            {text}
        </div>
        """, unsafe_allow_html=True)

def display_research_ui(research: ResearchContext):
    """Display all research components with proper layout"""
    # Main content columns
    main_col, sidebar_col = st.columns([7, 3], gap="large")
    
    with main_col:
        # Research Header
        st.markdown(f"## 📌 Current Research: {research.query}")
        if research.last_updated:
            st.caption(f"Last updated: {research.last_updated.strftime('%Y-%m-%d %H:%M')}")
        
        # AI Analysis
        st.markdown("### 📝 Comprehensive Analysis")
        display_response(research.ai_response)
        st.markdown("---")
        
        # News Section
        if research.news:
            st.markdown("### 🗞️ Latest News")
            for article in research.news:
                with st.expander(f"{article.date}: {article.title}"):
                    if article.image:
                        st.image(article.image, use_column_width=True)
                    st.write(article.description or "No description available")
                    st.markdown(f"[Read at {article.source}]({article.url})")
            st.markdown("---")