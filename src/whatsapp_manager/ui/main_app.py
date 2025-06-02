# Third-party library imports
import streamlit as st

st.set_page_config(page_title='WhatsApp Group Resumer', layout='wide')

# --- Light Theme CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* --- Light Professional Theme --- */

/* Base Styles */
body, .stApp {
    background-color: #FFFFFF; /* White Background */
    font-family: 'Inter', sans-serif;
    color: #1E1E1E; /* Dark Gray Text */
    font-size: 16px;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #1E1E1E; /* Dark Gray */
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 0.8em;
    line-height: 1.3;
}
h1.landing-title { /* Specific class for landing page title */
    font-size: 3.2em; /* Larger title */
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.4em;
    color: #0D6EFD; /* Professional Blue */
}
p.landing-subtitle { /* Specific class for landing page subtitle */
    font-size: 1.35em;
    color: #555555; /* Medium Gray */
    text-align: center;
    margin-bottom: 3em;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}
h2 { font-size: 1.8em; color: #0D6EFD; border-bottom: 2px solid #E0E0E0; padding-bottom: 0.3em; }
h3 { font-size: 1.4em; color: #333333; margin-bottom: 0.5em; }

/* Main Content Area */
.main > div { padding-top: 3rem; }
.block-container { max-width: 1100px; padding-left: 2rem; padding-right: 2rem; }

/* Feature Cards */
.feature-card {
    background-color: #FFFFFF; /* White Background */
    border-radius: 12px;
    padding: 30px 35px;
    margin-bottom: 25px;
    color: #1E1E1E;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); /* Softer shadow */
    border: 1px solid #E0E0E0; /* Light border */
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    text-align: center;
    height: 100%; /* Make cards in a row equal height */
}
 .feature-card:hover {
    box-shadow: 0 6px 20px rgba(13, 110, 253, 0.15); /* Blue shadow on hover */
    transform: translateY(-5px);
 }
 .feature-card h3 {
     color: #0D6EFD; /* Blue Accent for feature titles */
     font-size: 1.6em;
     margin-bottom: 0.6em;
     border: none;
     padding-left: 0;
 }
 .feature-card p {
     color: #444444; /* Darker gray for feature description */
     font-size: 1.05em;
 }
 .feature-card .emoji {
     font-size: 2.5em; /* Larger emoji */
     margin-bottom: 0.5em;
     display: block;
 }

/* Sidebar */
.css-1d391kg { /* Sidebar container */
    background-color: #FFFFFF !important; /* White Sidebar */
    border-right: 1px solid #E0E0E0; /* Light separator */
    padding-top: 1rem;
}
.css-1d391kg .css-1v3fvcr { /* Sidebar links */
    color: #333333; /* Dark Gray */
    border-radius: 8px;
    margin: 5px 10px;
    padding: 12px 20px;
    font-size: 1.05em;
    transition: background-color 0.2s ease, color 0.2s ease;
    border-left: 3px solid transparent;
}
.css-1d391kg .css-1v3fvcr:hover {
    background-color: #F0F2F6; /* Light Gray background on hover */
    color: #0D6EFD; /* Blue on hover */
}
.css-1d391kg .st-emotion-cache-1aehpvj { /* Active page link */
    background-color: #F0F2F6;
    color: #0D6EFD !important; /* Blue */
    font-weight: 600;
    border-left: 3px solid #0D6EFD; /* Active indicator */
}

/* Buttons (Keep consistent, adapt for light theme) */
.stButton>button {
    background-color: #0D6EFD; /* Blue */
    color: #FFFFFF; /* White text */
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1.05em;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
    margin-bottom: 10px;
    transition: background-color 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease;
}
.stButton>button:hover {
    background-color: #0B5ED7; /* Darker Blue on hover */
    box-shadow: 0 4px 10px rgba(13, 110, 253, 0.3);
    transform: translateY(-1px);
}
 .stButton>button:active {
     transform: translateY(0px);
     box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
 }

/* Inputs & Selects (Adapt for light theme) */
.stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF; /* White background */
    border: 1.5px solid #CED4DA; /* Standard input border */
    border-radius: 8px;
    color: #1E1E1E !important; /* Dark text */
    padding: 12px;
    font-size: 1em;
    margin-bottom: 12px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stSelectbox div[data-baseweb="select"] span { color: #1E1E1E !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder, .stSelectbox input::placeholder { color: #6C757D !important; opacity: 1 !important; }
.stTextInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus, .stTimeInput input:focus,
.stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: #86B7FE; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); outline: none; }
div[data-baseweb="popover"] ul[role="listbox"] { background-color: #FFFFFF; border: 1px solid #CED4DA; color: #1E1E1E; }
div[data-baseweb="popover"] li[role="option"]:hover { background-color: #F0F2F6; }

/* Checkbox (Adapt for light theme) */
.stCheckbox label span { color: #1E1E1E !important; font-size: 1em; padding-left: 8px; }
.stCheckbox input[type="checkbox"] { accent-color: #0D6EFD; width: 1.3em; height: 1.3em; margin-right: 5px; }

/* Alerts (Adapt for light theme) */
.stAlert { border-radius: 8px; border-left-width: 6px !important; padding: 16px; margin: 16px 0; font-size: 1em; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); }
.stAlert[data-testid="stAlert"] > div[role="alert"][data-baseweb="alert"][kind="info"] { background-color: #CCE5FF; border-color: #0D6EFD; color: #052C65; }
.stAlert[data-testid="stAlert"] > div[role="alert"][data-baseweb="alert"][kind="warning"] { background-color: #FFF3CD; border-color: #FFC107; color: #664D03; }
.stAlert[data-testid="stAlert"] > div[role="alert"][data-baseweb="alert"][kind="success"] { background-color: #D1E7DD; border-color: #198754; color: #0A3622; }
.stAlert[data-testid="stAlert"] > div[role="alert"][data-baseweb="alert"][kind="error"] { background-color: #F8D7DA; border-color: #DC3545; color: #58151C; }

/* Tabs (Adapt for light theme) */
.stTabs [data-baseweb="tab-list"] { background-color: transparent; padding: 0; margin-bottom: 20px; border-bottom: 2px solid #DEE2E6; }
.stTabs [data-baseweb="tab"] { background-color: transparent; color: #495057; border-radius: 6px 6px 0 0; margin: 0 4px; padding: 10px 20px; font-size: 1.05em; font-weight: 600; transition: background-color 0.2s ease, color 0.2s ease; border: none; border-bottom: 3px solid transparent; position: relative; bottom: -2px; }
.stTabs [data-baseweb="tab"]:hover { background-color: #F0F2F6; color: #0D6EFD; }
.stTabs [aria-selected="true"] { background-color: #F0F2F6; color: #0D6EFD !important; border-bottom: 3px solid #0D6EFD; }

/* Utility: Add more space below inputs */
.stTextInput, .stTextArea, .stDateInput, .stTimeInput, .stSelectbox, .stCheckbox { margin-bottom: 20px !important; }
</style>
""",
    unsafe_allow_html=True
)

# --- Landing Page Content ---

st.markdown('<h1 class="landing-title">WhatsApp Group Resumer</h1>', unsafe_allow_html=True)
st.markdown('''<p class="landing-subtitle">
    Gerencie seus grupos do WhatsApp e agende resumos inteligentes de forma automática e eficiente. <br>
    Manage your WhatsApp groups and schedule smart summaries automatically and efficiently.
</p>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Add some space

# Feature Highlight Section
cols = st.columns(3, gap="large")

with cols[0]:
    st.markdown('''
    <div class="feature-card">
        <span class="emoji">👥</span>
        <h3>Gestão de Grupos / Group Management</h3>
        <p>Visualize e selecione facilmente os grupos do WhatsApp que deseja gerenciar.<br>
        Easily view and select the WhatsApp groups you want to manage.</p>
    </div>
    ''', unsafe_allow_html=True)

with cols[1]:
    st.markdown('''
    <div class="feature-card">
        <span class="emoji">📅</span>
        <h3>Agendamento Inteligente / Smart Scheduling</h3>
        <p>Configure resumos automáticos diários para grupos específicos nos horários desejados.<br>
        Set up automatic daily summaries for specific groups at your preferred times.</p>
    </div>
    ''', unsafe_allow_html=True)

with cols[2]:
    st.markdown('''
    <div class="feature-card">
        <span class="emoji">🧠</span>
        <h3>Resumos com IA / AI Summaries</h3>
        <p>Obtenha resumos concisos e relevantes do conteúdo das conversas, com opções de personalização.<br>
        Get concise and relevant summaries of conversation content, with customization options.</p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---") # Separator

st.info("👈 Utilize o menu na barra lateral para navegar entre as versões em Português e Inglês e começar a usar a aplicação. / Use the sidebar menu to navigate between Portuguese and English versions and start using the application.")

# Add a note about navigation in the sidebar as well
st.sidebar.success("Bem-vindo! / Welcome! Selecione um idioma. / Select a language.")