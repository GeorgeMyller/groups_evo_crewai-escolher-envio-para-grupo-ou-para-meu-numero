import streamlit as st
from group_controller import GroupController

st.set_page_config(page_title='Group Management & Scheduling App', layout='wide')

# Initialize group controller
controller = GroupController()

# Inject custom CSS for a modern, elegant design with Google Fonts and Font Awesome
st.markdown(
  """
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

  body, .stApp {
    background: linear-gradient(135deg, #0a0f1a 0%, #1a2233 100%) !important;
    min-height: 10vh;
    font-family: 'Orbitron', sans-serif;
  }

  /* Reduz o espaço do topo */
  .main-landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 8vh;
    padding: 2px 0 4px 0;
  }

  h1.title {
    color: #39FF14;
    text-align: center;
    margin-top: 0;
    margin-bottom: 14px;
    font-size: 2.5em;
    letter-spacing: 2px;
    /* Removido o animation: glow */
    text-shadow: none;
  }
  /* Removido o @keyframes glow */
  p.subtitle {
    color: #FF5F1F;
    font-size: 1.2em;
    text-align: center;
    margin-bottom: 24px;
  }
  .content {
    background: rgba(10, 15, 26, 0.92);
    border-radius: 18px;
    box-shadow: 0 0 32px #00FFAA44;
    padding: 38px 28px 28px 28px;
    margin: 0 auto 24px auto;
    max-width: 600px;
    color: #E0E0E0;
    text-align: center;
    transition: box-shadow 0.3s, transform 0.3s;
  }
  .content:hover {
    box-shadow: 0 0 48px #00BBFF88;
    transform: translateY(-2px) scale(1.01);
  }
  /* Destaque para as abas (tabs) */
  .stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    margin-bottom: 18px;
    gap: 18px;
  }
  .stTabs [data-baseweb="tab"] {
    background: rgba(20, 30, 50, 0.7);
    border-radius: 12px 12px 0 0;
    color: #00E5FF;
    font-size: 1.1em;
    font-weight: 700;
    padding: 0.7em 2.2em;
    margin: 0 2px;
    border: 2px solid transparent;
    box-shadow: 0 0 8px #00FFAA33;
    transition: background 0.2s, color 0.2s, box-shadow 0.2s, border 0.2s;
    position: relative;
    z-index: 1;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #112233 0%, #223344 100%);
    color: #fff;
    border: 2px solid #00FFAA44;
    box-shadow: none;
    animation: none;
    z-index: 2;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 18px #00FFAA99, 0 0 8px #FF5F1F55; }
    50% { box-shadow: 0 0 32px #00BBFF, 0 0 16px #FF5F1F; }
    100% { box-shadow: 0 0 18px #00FFAA99, 0 0 8px #FF5F1F55; }
  }
  </style>
  """,
  unsafe_allow_html=True
)

# Centraliza e amplia o conteúdo principal
st.markdown('<div class="main-landing">', unsafe_allow_html=True)
st.markdown('<h1 class="title">Bem-vindo ao WhatsApp Group Resumer App</h1>', unsafe_allow_html=True)

# Tabs para idiomas
st.markdown('<div style="width:100%;max-width:650px;margin:0 auto;">', unsafe_allow_html=True)
tabs = st.tabs(["Versão em Português", "English Version"])

with tabs[0]:
  st.markdown('<p class="subtitle">Uma experiência centrada no usuário para gerenciar grupos e agendar resumos de forma prática.</p>', unsafe_allow_html=True)
  st.markdown('''
  <div class="content tab-content">
    <h3>O que o Programa Faz?</h3>
    <p>Este programa permite que você visualize detalhes dos grupos, agende a geração de resumos automáticos e os envie para grupos ou contatos pessoais. Nossa interface intuitiva foi desenvolvida para oferecer uma experiência agradável e eficiente.</p>
    <h3>Como Funciona?</h3>
    <p>Após carregar os dados dos grupos, você pode selecionar um grupo específico, visualizar suas informações e configurar o agendamento do resumo. Escolha entre agendamentos diários ou uma execução única, e o sistema cuida do restante automaticamente.</p>
    <br/>
  </div>
  ''', unsafe_allow_html=True)

with tabs[1]:
  st.markdown('<p class="subtitle">A user-centered experience to manage groups and schedule automated summaries effortlessly.</p>', unsafe_allow_html=True)
  st.markdown('''
  <div class="content tab-content">
    <h3>What Does This Program Do?</h3>
    <p>This program allows you to view detailed group information, schedule automated summary generation, and send these summaries to groups or personal contacts. Our intuitive interface is designed to provide an efficient and enjoyable experience.</p>
    <h3>How It Works?</h3>
    <p>After loading group data, you can select a specific group, view its details, and configure summary scheduling. Choose between daily or one-time tasks, and the system automatically handles the rest.</p>
    <br/>
  </div>
  ''', unsafe_allow_html=True)
  

