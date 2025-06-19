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
    font-weight: 500;
    text-decoration: none;
    transition: all 0.3s ease;
}
.css-1d391kg .css-1v3fvcr:hover { /* Sidebar link hover */
    background-color: #F8F9FA; /* Very Light Gray */
    color: #0D6EFD; /* Blue on hover */
    transform: translateX(5px);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0D6EFD 0%, #0056D2 100%); /* Blue Gradient */
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 1.05em;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0056D2 0%, #003D99 100%); /* Darker Blue Gradient */
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(13, 110, 253, 0.4);
}
.stButton > button:active {
    transform: translateY(0px);
    box-shadow: 0 3px 8px rgba(13, 110, 253, 0.3);
}

/* Input Fields */
.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div > div {
    border: 2px solid #E0E0E0; /* Light Gray Border */
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 1em;
    font-family: 'Inter', sans-serif;
    color: #1E1E1E;
    background-color: #FFFFFF;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus, .stSelectbox > div > div > div:focus {
    border-color: #0D6EFD; /* Blue Border on Focus */
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1); /* Blue Shadow */
    outline: none;
}

/* Metrics and Info Boxes */
.metric-container {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Success/Error Messages */
.stAlert {
    border-radius: 8px;
    border: none;
    padding: 16px 20px;
    margin: 16px 0;
}
.stAlert[data-baseweb="notification"] {
    background-color: #D4EDDA; /* Light Green Background */
    color: #155724; /* Dark Green Text */
    border-left: 4px solid #28A745; /* Green Left Border */
}

/* Data Tables */
.stDataFrame {
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    overflow: hidden;
}
.stDataFrame table {
    font-family: 'Inter', sans-serif;
    font-size: 0.95em;
}
.stDataFrame thead th {
    background-color: #F8F9FA; /* Light Gray Header */
    color: #333333;
    font-weight: 600;
    border-bottom: 2px solid #E0E0E0;
    padding: 12px 16px;
}
.stDataFrame tbody td {
    padding: 10px 16px;
    border-bottom: 1px solid #F0F0F0;
}
.stDataFrame tbody tr:hover {
    background-color: #F8F9FA; /* Light Gray on Hover */
}

/* Loading Spinner */
.stSpinner > div {
    border-top-color: #0D6EFD !important; /* Blue Spinner */
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #F8F9FA;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    color: #333333;
    font-weight: 600;
}
.streamlit-expanderContent {
    border: 1px solid #E0E0E0;
    border-top: none;
    border-radius: 0 0 8px 8px;
    background-color: #FFFFFF;
}

/* Progress Bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #0D6EFD 0%, #28A745 100%);
}

/* File Uploader */
.stFileUploader {
    border: 2px dashed #E0E0E0;
    border-radius: 12px;
    padding: 40px 20px;
    text-align: center;
    background-color: #FAFAFA;
    transition: all 0.3s ease;
}
.stFileUploader:hover {
    border-color: #0D6EFD;
    background-color: #F0F7FF;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #E0E0E0;
}
.stTabs [data-baseweb="tab"] {
    color: #666666;
    font-weight: 500;
    padding: 12px 24px;
    border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #0D6EFD;
    background-color: #F0F7FF;
    border-bottom: 3px solid #0D6EFD;
}

/* Code Blocks */
.stCode {
    background-color: #F8F9FA;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    font-family: 'Roboto Mono', monospace;
}

/* Responsive Design */
@media (max-width: 768px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    h1.landing-title { font-size: 2.5em; }
    p.landing-subtitle { font-size: 1.2em; }
}
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="landing-title">🤖 WhatsApp Group Resumer</h1>', unsafe_allow_html=True)
st.markdown('<p class="landing-subtitle">Inteligência Artificial para Resumir e Gerenciar Grupos do WhatsApp / AI-Powered WhatsApp Group Summary and Management</p>', unsafe_allow_html=True)

# Feature Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="emoji">📊</div>
        <h3>Resumos Inteligentes</h3>
        <p>Crie resumos automáticos das conversas dos seus grupos do WhatsApp usando IA avançada.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="emoji">⚡</div>
        <h3>Agendamento Automático</h3>
        <p>Configure resumos automáticos para serem gerados e enviados periodicamente.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="emoji">🌐</div>
        <h3>Múltiplos Idiomas</h3>
        <p>Interface disponível em Português e Inglês, com suporte completo para ambos os idiomas.</p>
    </div>
    """, unsafe_allow_html=True)

# Getting Started Section
st.markdown("## 🚀 Como Começar / Getting Started")

st.markdown("""
### PT-BR - Português
1. **Configure sua API**: Acesse a página "Portuguese" no menu lateral
2. **Conecte ao WhatsApp**: Configure suas credenciais da Evolution API
3. **Selecione Grupos**: Escolha os grupos que deseja resumir
4. **Gere Resumos**: Crie resumos manuais ou configure agendamento automático

### EN - English  
1. **Configure your API**: Access the "English" page in the sidebar
2. **Connect to WhatsApp**: Set up your Evolution API credentials
3. **Select Groups**: Choose which groups you want to summarize
4. **Generate Summaries**: Create manual summaries or set up automatic scheduling
""")

# Status Section
st.markdown("## 📊 Status do Sistema / System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔌 Conexão API / API Connection",
        value="Verificando... / Checking...",
        help="Status da conexão com a Evolution API"
    )

with col2:
    st.metric(
        label="📱 Grupos Ativos / Active Groups", 
        value="0",
        help="Número de grupos configurados para resumo"
    )

with col3:
    st.metric(
        label="📝 Resumos Hoje / Today's Summaries",
        value="0", 
        help="Resumos gerados hoje"
    )

with col4:
    st.metric(
        label="⏰ Próximo Agendado / Next Scheduled",
        value="N/A",
        help="Próximo resumo agendado"
    )

# Quick Actions
st.markdown("## ⚡ Ações Rápidas / Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Verificar Conexão API / Check API Connection", use_container_width=True):
        st.info("Funcionalidade será implementada na página específica do idioma / Feature will be implemented in language-specific page")

with col2:
    if st.button("📊 Ver Dashboard Completo / View Full Dashboard", use_container_width=True):
        st.info("Acesse a página Dashboard no menu lateral / Access Dashboard page in sidebar")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666666; padding: 20px 0;">
    <p><strong>WhatsApp Group Resumer</strong> | Powered by Evolution API & CrewAI</p>
    <p>Desenvolvido com ❤️ para simplificar o gerenciamento de grupos do WhatsApp</p>
    <p>Developed with ❤️ to simplify WhatsApp group management</p>
</div>
""", unsafe_allow_html=True)
