import streamlit as st
import os
import pandas as pd
from datetime import time, date, datetime, timedelta
import time as t  # Renomeado para evitar conflito
from dotenv import load_dotenv

# Set page config first
st.set_page_config(page_title='Gerenciamento e Agendamento (PT)', layout='wide')

# Load environment variables relative to the main app.py directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# st.write(f"Carregando .env de: {env_path}") # Comentado para não poluir a UI
load_dotenv(env_path)

# Import project modules using relative paths
from group_controller import GroupController
from groups_util import GroupUtils
from task_scheduler import TaskScheduled
from send_sandeco import SendSandeco

# Inject consistent CSS (light theme)
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

    .main-content-area { /* Changed class name */
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 16px;
      margin: 0;
    }

    h1.page-title { /* Changed class name */
      color: #2c3e50;
      font-size: 2.2em; /* Slightly smaller for page title */
      margin: 0 0 16px;
      text-align: center;
      font-weight: 700;
    }

    /* Styling for columns and headers */
    .stColumn {
        padding: 0 10px; /* Add some padding between columns */
    }
    h2, h3, .stSubheader {
        color: #34495e;
    }

    /* Expander styling */
    .stExpander {
        border: 1px solid #dcdde1;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
    .stExpander header {
        font-weight: 600;
        color: #3498db;
    }

    /* Button styling */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stButton>button[kind="secondary"] { /* Style for secondary buttons like 'Remove' */
        background-color: #e74c3c;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #c0392b;
    }

    /* Input widgets styling */
    .stTextInput, .stSelectbox, .stCheckbox, .stDateInput, .stTimeInput {
        margin-bottom: 10px;
    }

    /* Group details styling */
    .group-details img {
        border-radius: 50%;
        margin-right: 15px;
        vertical-align: middle;
    }
    .group-details span {
        font-size: 1.1em;
        font-weight: 600;
        color: #2c3e50;
    }
    .group-info p {
        margin: 5px 0;
        color: #555;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- Core Logic Functions ---

# Initialize core components
control = GroupController()
ut = GroupUtils()
sender = SendSandeco()

# Define file paths relative to the main project directory
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'group_summary.csv')
CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', 'groups_cache.json')
PYTHON_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'summary.py')

def load_scheduled_groups():
    """Carrega grupos agendados ativos do CSV."""
    try:
        df = pd.read_csv(CSV_PATH)
        return df[df['enabled'] == True]
    except FileNotFoundError:
        # Create the file with headers if it doesn't exist
        pd.DataFrame(columns=['group_id', 'horario', 'enabled', 'is_links', 'is_names', 'send_to_group', 'send_to_personal', 'script', 'start_date', 'end_date', 'start_time', 'end_time']).to_csv(CSV_PATH, index=False)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar agendamentos: {e}")
        return pd.DataFrame()

def delete_scheduled_group(group_id):
    """Remove um grupo agendado do CSV e tarefas do sistema."""
    try:
        df = pd.read_csv(CSV_PATH)
        if group_id not in df['group_id'].values:
            st.error(f"Grupo com ID {group_id} não encontrado no CSV!")
            return False

        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            st.success(f"Tarefa {task_name} removida do sistema.")
        except Exception as e:
            # Don't stop the process if task deletion fails (might not exist)
            st.warning(f"Aviso: Não foi possível remover a tarefa agendada '{task_name}' (pode já ter sido removida ou não existir): {e}")

        df = df[df['group_id'] != group_id]
        df.to_csv(CSV_PATH, index=False)
        st.success(f"Agendamento para o grupo {group_id} removido do arquivo de configuração.")
        return True
    except FileNotFoundError:
        st.error("Arquivo group_summary.csv não encontrado.")
        return False
    except Exception as e:
        st.error(f"Erro ao remover agendamento do grupo {group_id}: {e}")
        return False

# --- Streamlit UI --- 

st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Gerenciamento de Grupos & Agendamento</h1>', unsafe_allow_html=True)

# Botão para atualizar grupos manualmente
if st.sidebar.button('Atualizar Lista de Grupos'):
    with st.spinner('Atualizando grupos...'):
        # Pass cache path to controller
        control.fetch_groups(force_refresh=True)
    st.sidebar.success('Grupos atualizados com sucesso!')
    st.rerun() # Rerun to reflect changes

# Carrega lista de grupos (usa cache padrão ou atualizado)
groups = control.fetch_groups()
group_map, options = ut.map(groups)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Selecione um Grupo")
    if group_map:
        # Dropdown para selecionar grupo
        selected_option = st.selectbox(
            "Escolha um grupo:",
            options,
            format_func=lambda x: x[0], # Mostra apenas o nome no dropdown
            key="pt_group_select" # Unique key for this widget
        )
        selected_group_id = selected_option[1] # Pega o ID da opção selecionada
        selected_group = group_map[selected_group_id]

        # Exibe detalhes do grupo selecionado
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(f'<div class="group-details">{head_group}</div>', unsafe_allow_html=True)
        with st.expander("Detalhes do Grupo", expanded=False):
            ut.group_details(selected_group)

        # Seção de Tarefas Agendadas
        st.subheader("Tarefas Agendadas Ativas")
        scheduled_groups_df = load_scheduled_groups()

        if not scheduled_groups_df.empty:
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []

            for _, row in scheduled_groups_df.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, f"ID: {group_id}") # Fallback para ID se nome não encontrado
                horario = row.get('horario', 'N/A')
                start_date_str = row.get('start_date')
                end_date_str = row.get('end_date')
                start_time_str = row.get('start_time')
                end_time_str = row.get('end_time')

                # Determina a periodicidade baseada nos campos preenchidos
                if horario and not start_date_str:
                    periodicidade = f"Diariamente às {horario}"
                elif start_date_str and start_time_str:
                    if (not start_date_str or start_date_str == 'nan' or pd.isna(start_date_str) or
                        not start_time_str or start_time_str == 'nan' or pd.isna(start_time_str)):
                        periodicidade = "Uma vez (data/horário não definido)"
                    else:
                        periodicidade = f"Uma vez em {start_date_str} às {start_time_str}"
                else:
                    periodicidade = "Indefinida"

                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "horario_ou_data": horario if horario and not start_date_str else f"{start_date_str} {start_time_str}",
                    "periodicidade": periodicidade,
                    "display_text": f"{group_name} - {periodicidade}"
                })

            # Dropdown para selecionar tarefa agendada
            options_list = [info['display_text'] for info in scheduled_groups_info]
            if options_list:
                selected_task_idx = st.selectbox("Grupos com Resumos Agendados:",
                                               range(len(options_list)),
                                               format_func=lambda x: options_list[x],
                                               key="pt_scheduled_select")

                if selected_task_idx is not None:
                    selected_info = scheduled_groups_info[selected_task_idx]
                    st.write(f"**Grupo:** {selected_info['name']}")
                    st.write(f"**ID:** {selected_info['id']}")
                    st.write(f"**Agendamento:** {selected_info['periodicidade']}")

                    # Botão para remover agendamento
                    if st.button("Remover Agendamento", key=f"remove_pt_{selected_info['id']}", type="secondary"):
                        if delete_scheduled_group(selected_info['id']):
                            st.success(f"Agendamento para {selected_info['name']} removido.")
                            t.sleep(1) # Pausa breve para usuário ver a mensagem
                            st.rerun()
                        else:
                            st.error("Falha ao remover o agendamento.")
            else:
                st.info("Não há grupos com resumos agendados ativos.")
        else:
            st.info("Não há grupos com resumos agendados ativos.")
    else:
        st.warning("Nenhum grupo encontrado! Tente atualizar a lista.")

with col2:
    if group_map and selected_group: # Garante que um grupo foi selecionado
        st.header("Configurações de Resumo")
        with st.expander("Ajustar Agendamento e Opções", expanded=True):

            # Carrega configurações salvas para o grupo selecionado, se existirem
            saved_config_df = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()
            group_config = saved_config_df[saved_config_df['group_id'] == selected_group_id]
            current_config = group_config.iloc[0].to_dict() if not group_config.empty else {}

            # --- Formulário de Configuração ---
            enabled = st.checkbox("Habilitar Geração do Resumo",
                                value=current_config.get('enabled', False), # Default para False se não configurado
                                key=f"pt_enable_{selected_group_id}")

            periodicidade = st.selectbox("Periodicidade",
                                       ["Diariamente", "Uma vez"],
                                       index=0 if not current_config.get('start_date') else 1,
                                       key=f"pt_freq_{selected_group_id}")

            horario = None
            start_date, end_date, start_time, end_time = None, None, None, None

            if periodicidade == "Diariamente":
                default_time_str = current_config.get('horario', "09:00")
                try:
                    default_time = datetime.strptime(default_time_str, "%H:%M").time()
                except (ValueError, TypeError):
                    default_time = time(9, 0) # Fallback
                horario = st.time_input("Horário de Execução Diária:",
                                      value=default_time,
                                      key=f"pt_time_{selected_group_id}")
            else: # Periodicidade == "Uma vez"
                col_start, col_end = st.columns(2)
                with col_start:
                    default_start_date_str = current_config.get('start_date', date.today().strftime('%Y-%m-%d'))
                    try:
                        default_start_date = datetime.strptime(default_start_date_str, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        default_start_date = date.today()
                    # Garante que a data padrão nunca é menor que o mínimo permitido
                    if default_start_date < date.today():
                        default_start_date = date.today()
                    start_date = st.date_input("Data de Início:",
                                             value=default_start_date,
                                             min_value=date.today(),
                                             key=f"pt_start_date_{selected_group_id}")

                    default_start_time_str = current_config.get('start_time', (datetime.now() + timedelta(minutes=5)).strftime('%H:%M'))
                    try:
                        default_start_time = datetime.strptime(default_start_time_str, '%H:%M').time()
                    except (ValueError, TypeError):
                        default_start_time = (datetime.now() + timedelta(minutes=5)).time()
                    start_time = st.time_input("Hora de Início:",
                                             value=default_start_time,
                                             key=f"pt_start_time_{selected_group_id}")
                # Campos End Date/Time (opcional, não usado atualmente para "Uma Vez")
                # with col_end:
                #     end_date = st.date_input("Data de Fim:", value=start_date + timedelta(days=1), min_value=start_date)
                #     end_time = st.time_input("Hora de Fim:", value=time(23, 59))

            is_links = st.checkbox("Incluir Links no Resumo",
                                 value=current_config.get('is_links', True),
                                 key=f"pt_links_{selected_group_id}")
            is_names = st.checkbox("Incluir Nomes no Resumo",
                                 value=current_config.get('is_names', True),
                                 key=f"pt_names_{selected_group_id}")

            send_to_group = st.checkbox("Enviar Resumo para o Grupo",
                                      value=current_config.get('send_to_group', True),
                                      key=f"pt_send_group_{selected_group_id}")
            send_to_personal = st.checkbox("Enviar Resumo para o Meu Celular",
                                         value=current_config.get('send_to_personal', False),
                                         key=f"pt_send_personal_{selected_group_id}")

            # Botão Salvar Configurações
            if st.button("Salvar Configurações", key=f"save_pt_{selected_group_id}"):
                task_name = f"ResumoGrupo_{selected_group.group_id}"
                config_data = {
                    'group_id': selected_group.group_id,
                    'enabled': enabled,
                    'is_links': is_links,
                    'is_names': is_names,
                    'send_to_group': send_to_group,
                    'send_to_personal': send_to_personal,
                    'script': PYTHON_SCRIPT_PATH,
                    'horario': horario.strftime("%H:%M") if horario else None,
                    'start_date': start_date.strftime("%Y-%m-%d") if start_date else None,
                    'end_date': end_date.strftime("%Y-%m-%d") if end_date else None,
                    'start_time': start_time.strftime("%H:%M") if start_time else None,
                    'end_time': end_time.strftime("%H:%M") if end_time else None
                }

                try:
                    # Atualiza ou adiciona a configuração no CSV
                    if os.path.exists(CSV_PATH):
                        df = pd.read_csv(CSV_PATH)
                    else:
                        df = pd.DataFrame(columns=config_data.keys())

                    if selected_group.group_id in df['group_id'].values:
                        # Atualiza linha existente
                        idx = df.index[df['group_id'] == selected_group.group_id].tolist()[0]
                        for key, value in config_data.items():
                            df.loc[idx, key] = value
                    else:
                        # Adiciona nova linha
                        new_row = pd.DataFrame([config_data])
                        df = pd.concat([df, new_row], ignore_index=True)

                    df.to_csv(CSV_PATH, index=False)
                    st.success("Configurações salvas no arquivo CSV!")

                    # Gerencia a tarefa agendada
                    if enabled:
                        if periodicidade == "Diariamente" and horario:
                            TaskScheduled.create_task(
                                task_name=task_name,
                                python_script_path=PYTHON_SCRIPT_PATH,
                                schedule_type='DAILY',
                                time=horario.strftime("%H:%M")
                            )
                            st.success(f"Agendamento diário configurado para as {horario.strftime('%H:%M')}!")
                        elif periodicidade == "Uma vez" and start_date and start_time:
                            # Combina data e hora para criar datetime
                            run_datetime = datetime.combine(start_date, start_time)
                            # Verifica se a hora já passou hoje
                            now = datetime.now()
                            if run_datetime <= now:
                                st.error("A data e hora selecionadas para execução única já passaram. Escolha um horário futuro.")
                            else:
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=PYTHON_SCRIPT_PATH,
                                    schedule_type='ONCE',
                                    date=start_date.strftime("%Y-%m-%d"),
                                    time=start_time.strftime("%H:%M")
                                )
                                st.success(f"Agendamento único configurado para {start_date.strftime('%d/%m/%Y')} às {start_time.strftime('%H:%M')}!")
                        else:
                            st.warning("Configuração de agendamento incompleta (verifique horário/data).")
                    else: # Se não estiver habilitado, tenta remover tarefa existente
                        try:
                            TaskScheduled.delete_task(task_name)
                            st.info("Agendamento desativado e tarefa removida (se existia).")
                        except Exception:
                            st.info("Agendamento desativado (nenhuma tarefa encontrada para remover).")
                            pass # Não é um erro se a tarefa não existir

                    # Lógica de envio imediato para teste (opcional, pode ser removida)
                    # if send_to_personal:
                    #     personal_number = os.getenv('WHATSAPP_NUMBER')
                    #     if personal_number:
                    #         try:
                    #             sender.textMessage(number=personal_number, msg=f"Teste: Configuração salva para grupo {selected_group.name}.")
                    #             st.success("Mensagem de teste enviada para o seu celular!")
                    #         except Exception as send_err:
                    #             st.error(f"Erro ao enviar mensagem de teste: {send_err}")
                    #     else:
                    #         st.error("Número pessoal (WHATSAPP_NUMBER) não configurado no .env para envio de teste.")

                    t.sleep(1) # Pausa para usuário ler
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao salvar configurações ou agendar tarefa: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc()) # Mostra mais detalhes do erro

    else:
        st.info("Selecione um grupo na coluna à esquerda para ver as configurações.")

# Fecha o wrapper principal
st.markdown('</div>', unsafe_allow_html=True)