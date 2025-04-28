import streamlit as st

st.set_page_config(page_title='Group Management & Scheduling App', layout='wide')

# Inject custom CSS for a modern, elegant design with Google Fonts and Font Awesome
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    body, .stApp {
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
      font-family: 'Inter', sans-serif;
      color: #333;
      margin: 0;
      padding: 0;
    }

    .main-landing {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 16px;
      margin: 0;
    }

    h1.title {
      color: #2c3e50;
      font-size: 2.5em;
      margin: 0 0 16px;
      text-align: center;
      font-weight: 700;
      transition: transform 0.3s ease, color 0.3s ease;
    }
    h1.title:hover {
      transform: scale(1.05);
      color: #3498db;
    }
    p.subtitle {
      color: #34495e;
      font-size: 1.2em;
      margin: 0 0 24px;
      text-align: center;
    }

    .content {
      background: #ffffff;
      border: 1px solid #dcdde1;
      border-radius: 8px;
      padding: 24px;
      margin: 0 auto 24px;
      max-width: 700px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      text-align: left;
      line-height: 1.6;
      transition: box-shadow 0.3s ease, transform 0.3s ease;
    }
    .content:hover {
      box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
      transform: translateY(-5px);
    }

    .stTabs [data-baseweb="tab-list"] {
      justify-content: center;
      margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
      background: #ecf0f1;
      color: #2c3e50;
      font-weight: 600;
      padding: 0.5em 1.5em;
      border-radius: 4px;
      transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
      background: #3498db;
      color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# wrapper para centralizar todo conteúdo
st.markdown('<div class="main-landing">', unsafe_allow_html=True)
st.markdown('<h1 class="title">Bem-vindo ao WhatsApp Group Resumer App</h1>', unsafe_allow_html=True)

# Tabs para idiomas
tabs = st.tabs(["Versão em Português", "English Version"])

with tabs[0]:
    st.markdown('<p class="subtitle">Uma experiência centrada no usuário para gerenciar grupos e agendar resumos de forma prática.</p>', unsafe_allow_html=True)
    st.markdown('''
    <div class="content">
        <h3>O que o Programa Faz?</h3>
        <p>Este programa permite que você visualize detalhes dos grupos e agende resumos automáticos para grupos ou contatos pessoais com apenas alguns cliques.</p>
        <h3>Como Funciona?</h3>
        <p>Selecione um grupo, ajuste as configurações de resumo e deixe o sistema cuidar de todo o processo automaticamente.</p>
    </div>
    ''', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<p class="subtitle">A user-centered experience to manage groups and schedule automated summaries effortlessly.</p>', unsafe_allow_html=True)
    st.markdown('''
    <div class="content">
        <h3>What Does This Program Do?</h3>
        <p>This tool lets you view group details and schedule automated summaries to groups or personal contacts in just a few clicks.</p>
        <h3>How It Works?</h3>
        <p>Select a group, tweak summary settings, and let the system handle the rest automatically.</p>
    </div>
    ''', unsafe_allow_html=True)
# fecha o wrapper
st.markdown('</div>', unsafe_allow_html=True)