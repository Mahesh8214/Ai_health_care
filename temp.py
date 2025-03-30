import os
import requests
import google.generativeai as genai
from groq import Groq
import streamlit as st
from datetime import datetime, timedelta
import wikipedia
import time

# Set page config FIRST
st.set_page_config(
    page_title="Professional Research Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize APIs
GEMINI_API_KEY = "AIzaSyBGw47E4QS_xQXKEhVh_2F5u-bOpk-31wg"
GROQ_API_KEY = "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"
NEWS_API_KEY = "f0ebe21314e54bf59eaa87cdeb3f16be"

# Configure AI models
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
groq_client = Groq(api_key=GROQ_API_KEY)

# Custom CSS for dark follow-up responses and clean formatting
st.markdown("""
<style>
    .dark-response {
        background-color: #2d3748;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #4a5568;
    }
    .clean-text {
        font-family: Arial, sans-serif;
        line-height: 1.6;
    }
    .clean-text ul {
        padding-left: 1.5rem;
    }
    .clean-text li {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize all session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_research" not in st.session_state:
    st.session_state.current_research = {
        "query": "",
        "news": [],
        "wiki": "",
        "ai_response": "",
        "last_updated": None
    }
if "research_history" not in st.session_state:
    st.session_state.research_history = []
if "pending_followup" not in st.session_state:
    st.session_state.pending_followup = ""

def clean_response(text):
    """Remove markdown asterisks and clean formatting"""
    # Remove all asterisks
    text = text.replace("*", "")
    # Convert markdown bullets to HTML
    text = text.replace("- ", "• ")
    # Ensure proper line breaks
    text = text.replace("\n", "<br>")
    return text

def fetch_news(query, days_old=1):
    """Fetch and verify recent news with error handling"""
    try:
        date_from = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=5&sortBy=publishedAt&from={date_from}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        return [{
            "title": a["title"],
            "source": a["source"]["name"],
            "description": a.get("description"),
            "url": a["url"],
            "date": datetime.strptime(a["publishedAt"][:10], "%Y-%m-%d").strftime("%b %d, %Y"),
            "image": a.get("urlToImage")
        } for a in articles if a.get("title")]
    except Exception as e:
        st.error(f"⚠️ News API error: {str(e)}")
        return []

def get_wikipedia_summary(query):
    """Get concise Wikipedia summary with error handling"""
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return {"summary": "", "url": ""}
        
        page = wikipedia.page(search_results[0], auto_suggest=True)
        return {
            "summary": clean_response(page.summary[:500]) + f"... [Read more]({page.url})",
            "url": page.url
        }
    except Exception as e:
        st.error(f"⚠️ Wikipedia error: {str(e)}")
        return {"summary": "", "url": ""}

def generate_ai_response(query, context=""):
    """Generate comprehensive AI response with clean formatting"""
    try:
        prompt = f"""Generate a professional research response about: {query}
        Context: {context}
        Format requirements:
        - DO NOT use any asterisks (*) or markdown symbols
        - Use clear section headings followed by colons
        - Present bullet points as plain text with • symbols
        - Include relevant facts and sources
        
        Required sections:
        1. Key Findings: (3-5 main points)
        2. Current Status: (latest developments)
        3. Sources: (authoritative references)
        4. Next Steps: (suggested research directions)
        """
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.4
        )
        return clean_response(response.choices[0].message.content)
    except Exception as e:
        return f"⚠️ AI response error: {str(e)}"

def display_response(text, is_followup=False):
    """Display response with appropriate formatting"""
    if is_followup:
        st.markdown(f"""
        <div class="dark-response clean-text">
            {text}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="clean-text">
            {text}
        </div>
        """, unsafe_allow_html=True)

def process_new_query(query):
    """Handle new research queries with full state management"""
    if not query:
        return
    
    # Clear previous follow-up flag
    st.session_state.pending_followup = ""
    
    with st.spinner("🔍 Gathering the latest information..."):
        start_time = time.time()
        
        # Fetch all data components
        news = fetch_news(query)
        wiki_data = get_wikipedia_summary(query)
        context = f"News: {news}\nWikipedia: {wiki_data.get('summary', '')}"
        ai_response = generate_ai_response(query, context)
        
        # Update session state
        st.session_state.current_research = {
            "query": query,
            "news": news,
            "wiki": wiki_data.get("summary", ""),
            "ai_response": ai_response,
            "last_updated": datetime.now()
        }
        
        if query not in [q for q in st.session_state.research_history]:
            st.session_state.research_history.append(query)
        
        st.session_state.chat_history.append(("user", f"Research: {query}"))
        st.session_state.chat_history.append(("assistant", ai_response))
        
        st.toast(f"Research completed in {time.time() - start_time:.2f} seconds", icon="✅")

def process_followup(query):
    """Handle follow-up questions with context awareness"""
    if not query or query == st.session_state.pending_followup:
        return
    
    st.session_state.pending_followup = query
    current = st.session_state.current_research
    
    with st.spinner("💡 Analyzing your follow-up question..."):
        context = f"""
        Original Query: {current['query']}
        News: {current['news']}
        Wikipedia: {current['wiki']}
        Previous Analysis: {current['ai_response']}
        """
        
        response = generate_ai_response(query, context)
        
        # Update conversation history
        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("assistant", response))
        
        # Update current research with new insights
        st.session_state.current_research["ai_response"] = response
        st.rerun()

def display_current_research():
    """Display all research components with proper layout"""
    research = st.session_state.current_research
    
    # Main content columns
    main_col, sidebar_col = st.columns([7, 3], gap="large")
    
    with main_col:
        # Research Header
        st.markdown(f"## 📌 Current Research: {research['query']}")
        if research['last_updated']:
            st.caption(f"Last updated: {research['last_updated'].strftime('%Y-%m-%d %H:%M')}")
        
        # AI Analysis
        st.markdown("### 📝 Comprehensive Analysis")
        display_response(research["ai_response"])
        st.markdown("---")
        
        # News Section
        if research["news"]:
            st.markdown("### 🗞️ Latest News")
            for article in research["news"]:
                with st.expander(f"{article['date']}: {article['title']}"):
                    if article.get("image"):
                        st.image(article["image"], use_column_width=True)
                    st.write(article["description"] or "No description available")
                    st.markdown(f"[Read at {article['source']}]({article['url']})")
            st.markdown("---")
        
        # Wikipedia Summary
        if research["wiki"]:
            st.markdown("### 📚 Encyclopedia Context")
            st.markdown(research["wiki"])
    
    with sidebar_col:
        # Quick Facts
        st.markdown("### ⚡ Key Facts")
        if research["query"]:
            facts = groq_client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Extract 3 key facts about {research['query']} as plain text bullet points using • symbols"
                }],
                model="llama3-70b-8192",
                max_tokens=150
            )
            display_response(clean_response(facts.choices[0].message.content), is_followup=True)
        
        # Recent Topics
        st.markdown("---")
        st.markdown("### 🔍 Recent Topics")
        for i, topic in enumerate(st.session_state.research_history[-3:]):
            if st.button(f"{i+1}. {topic[:18]}..." if len(topic) > 20 else topic,
                       key=f"hist_{i}"):
                process_new_query(topic)
        
        # Follow-up Input
        st.markdown("---")
        st.markdown("### 💬 Continue Research")
        followup = st.text_input("Ask a follow-up question:", 
                                key="followup_input",
                                placeholder=f"Ask more about {research['query']}...")
        
        if followup:
            process_followup(followup)

def display_conversation_history():
    """Display the ongoing conversation thread"""
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
    for i, (role, message) in enumerate(st.session_state.chat_history[-6:]):
        if role == "user":
            st.markdown(f"""
            <div style='background-color:#f0f2f6; padding:12px; border-radius:8px; margin-bottom:8px;'>
                <strong>You:</strong> {message}
            </div>
            """, unsafe_allow_html=True)
        else:
            display_response(message, is_followup=True)

def main():
    # Main header
    st.markdown("""
    <div style='border-bottom:1px solid #eee; padding-bottom:1rem; margin-bottom:2rem;'>
        <h1 style='color:#1a73e8;'>🔬 Professional Research Agent</h1>
        <p>Get comprehensive, up-to-date information on any topic</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for new queries
    with st.sidebar:
        st.markdown("### 🚀 New Research Topic")
        new_query = st.text_input("Enter a topic to research:", key="new_query_input")
        if st.button("Start Research", type="primary", use_container_width=True):
            process_new_query(new_query)
    
    # Main content area
    if st.session_state.current_research["query"]:
        display_current_research()
        display_conversation_history()
    else:
        st.info("💡 Enter a research topic in the sidebar to begin")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#666; font-size:0.9rem; margin-top:2rem;'>
        <p>🔍 Powered by NewsAPI, Wikipedia, and Groq AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()