from data_pipeline.data_fetchers import fetch_news, get_wikipedia_summary
from ai_services.llm_clients import LLMClients
from interface.streamlit_ui import setup_page_config, display_research_ui
from data_pipeline.data_models import ResearchContext
import streamlit as st
import time
from datetime import datetime

def main():
    setup_page_config()
    llm = LLMClients()
    
    # Initialize session state
    if "research" not in st.session_state:
        st.session_state.research = None
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # UI Components
    st.title("🔬 Professional Research Agent")
    
    # Sidebar for new queries
    with st.sidebar:
        query = st.text_input("Enter research topic:")
        if st.button("Start Research"):
            with st.spinner("Gathering information..."):
                try:
                    news = fetch_news(query)
                    wiki = get_wikipedia_summary(query)
                    response = llm.get_groq_response(f"Analyze: {query}")
                    
                    st.session_state.research = ResearchContext(
                        query=query,
                        news=news,
                        wiki=wiki,
                        ai_response=response,
                        last_updated=datetime.now()
                    )
                    st.session_state.history.append(query)
                except Exception as e:
                    st.error(str(e))
    
    # Main display
    if st.session_state.research:
        display_research_ui(st.session_state.research)

if __name__ == "__main__":
    main()