import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import time

# --- Custom theme and styling ---
st.set_page_config(
    page_title="High-Growth Firm Insights",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        background-color: #f5f2ea !important;
    }
    
    /* Main title styling */
    .main-title {
        color: #2F6B69;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: center;
        padding: 1rem 0;
    }

    /* Section divider */
    .section-divider {
        border-top: 2px solid #2F6B69;
        margin: 2rem 0;
        opacity: 0.2;
    }

    /* Section title */
    .section-title {
        color: #2F6B69;
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* Chat message styling */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Form elements styling */
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #2F6B69;
        border-radius: 5px;
    }
    
    .stTextArea > div > div > textarea {
        background-color: white;
        border: 1px solid #2F6B69;
        border-radius: 5px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2F6B69;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #235352;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        color: #2F6B69;
        border-radius: 5px;
        border: 1px solid #2F6B69;
    }
    
    .streamlit-expanderContent {
        background-color: white;
        border-radius: 5px;
        padding: 1rem;
        margin-top: 0.5rem;
        border: 1px solid #2F6B69;
    }

    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #2F6B69;
    }

    /* Chat input styling */
    .stChatInputContainer {
        padding: 1rem 0;
    }

    /* Chat message colors */
    .stChatMessage [data-testid="chatAvatarIcon-user"] {
        background-color: #2F6B69;
    }
    
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
        background-color: #4A90E2;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Load environment variables ---
load_dotenv()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set your OpenAI API key in the .env file")
    st.stop()

# --- Load data ---
@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_excel("romania_hgfs.xlsx")
    return df

df = load_data()

def analyze_competitors(company_name, description, products_services, other_companies, top_n=5):
    # Limit the number of companies to analyze to reduce token usage
    MAX_COMPANIES = 20
    if len(other_companies) > MAX_COMPANIES:
        other_companies = other_companies[:MAX_COMPANIES]
    
    # Prepare company data for JSON serialization
    companies_data = []
    for company in other_companies:
        company_data = {
            "name": company["Company name Latin alphabet"],
            "description": company["Generated Description"][:300],
            "products_services": company["Products/Services"][:300] if pd.notna(company["Products/Services"]) else ""
        }
        companies_data.append(company_data)
    
    # Prepare a more concise prompt
    prompt = f"""
    Analyze this company and find its top {top_n} competitors from the list.
    
    Target Company:
    Name: {company_name}
    Description: {description[:500]}
    Products/Services: {products_services}
    
    Companies to analyze (max {MAX_COMPANIES}):
    {json.dumps(companies_data, indent=2)}
    
    Focus your analysis on:
    1. Direct product/service competition - Compare specific offerings
    2. Market overlap - Identify shared target markets and customer segments
    3. Technological similarity - Compare technological capabilities and solutions
    4. Service area overlap - Consider geographic presence and market reach
    
    For each competitor, provide:
    1. Similarity score (0-100) based on both description and products/services match
    2. Main reasons for competition, specifically mentioning matching products or services
    3. Key areas of overlap in both business description and specific offerings
    4. Areas where the companies differentiate themselves
    
    Return JSON with this structure:
    {{
        "competitors": [
            {{
                "company_name": "name",
                "similarity_score": number,
                "reasons": ["reason1", "reason2"],
                "overlap_areas": ["area1", "area2"],
                "differentiation_areas": ["area1", "area2"]
            }}
        ]
    }}
    """
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert business analyst specializing in competitive analysis.
                        Focus on concrete product/service overlaps and specific business capabilities when determining competitors.
                        Always return valid JSON and provide detailed, specific reasons for competition."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("Empty response from OpenAI")
            
            try:
                results = json.loads(content)
                if "competitors" not in results:
                    raise ValueError("Invalid response structure: missing 'competitors' key")
                return results
            except json.JSONDecodeError as e:
                st.error(f"Error parsing JSON response: {str(e)}")
                return None
                
        except Exception as e:
            if "rate_limit_exceeded" in str(e) and attempt < max_retries - 1:
                st.warning(f"Rate limit reached. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                st.error(f"Error in competitor analysis: {str(e)}")
                return None

def get_chatbot_response(user_query, company_data=None):
    try:
        context = ""
        if company_data is not None:
            context = f"""
            Current company context:
            Company: {company_data['Company name Latin alphabet']}
            Description: {company_data['Generated Description']}
            """

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a knowledgeable business analyst assistant. Provide concise, relevant answers about companies, competitors, and business strategy."},
                {"role": "user", "content": f"{context}\n\nUser question: {user_query}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- Page Layout ---
st.markdown('<h1 class="main-title">High-Growth Firm Competitor Analysis</h1>', unsafe_allow_html=True)

# Create company selector dropdown
company_names = df["Company name Latin alphabet"].tolist()
selected_company = st.selectbox(
    "Select a Company",
    options=company_names,
    index=0
)

# Get the description and products/services for the selected company
selected_company_data = df[df["Company name Latin alphabet"] == selected_company].iloc[0]
company_description = selected_company_data.get("Generated Description", "")
company_products = selected_company_data.get("Products/Services", "")

# Display the description in a text area that can be edited
description = st.text_area(
    "Company Description",
    value=f"{company_description}\n\nProducts/Services:\n{company_products}",
    height=150,
    help="You can edit the description if needed"
)

top_n = st.slider(
    "Number of Competitors",
    1, 5, 3,
    help="Select how many competitors you want to analyze"
)

if st.button("🔍 Find Competitors"):
    if description:
        with st.spinner("Analyzing competitors..."):
            # Get other companies for analysis
            other_companies = df[df["Company name Latin alphabet"] != selected_company][
                ["Company name Latin alphabet", "Generated Description", "Products/Services"]
            ].to_dict('records')
            
            # Get competitor analysis
            results = analyze_competitors(
                company_name=selected_company,
                description=company_description,
                products_services=company_products,
                other_companies=other_companies,
                top_n=top_n
            )
            
            if results and "competitors" in results:
                for competitor in results["competitors"]:
                    with st.expander(f"{competitor['company_name']} (Similarity: {competitor['similarity_score']}%)"):
                        st.write("**Key Reasons for Competition:**")
                        for reason in competitor["reasons"]:
                            st.write(f"- {reason}")
                        
                        st.write("**Areas of Overlap:**")
                        for area in competitor["overlap_areas"]:
                            st.write(f"- {area}")
                        
                        st.write("**Areas of Differentiation:**")
                        for area in competitor["differentiation_areas"]:
                            st.write(f"- {area}")
            else:
                st.error("No valid competitor analysis results were returned. Please try again.")
    else:
        st.warning("Please enter a brief description of the company.")

# Section Divider
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Knowledge Assistant Section
st.markdown('<h2 class="section-title">Knowledge Assistant</h2>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about companies and their competitors...", key="chat_input"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            response = get_chatbot_response(prompt, selected_company_data)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
