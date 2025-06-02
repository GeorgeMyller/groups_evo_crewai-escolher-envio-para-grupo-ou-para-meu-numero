import os
import time as t # Standard library time aliased
from datetime import time # datetime.time
from datetime import date # datetime.date
from datetime import datetime # datetime.datetime

# Third-party library imports
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Local application/library imports
# Define Project Root assuming this file is src/whatsapp_manager/ui/pages/2_Portuguese.py
# Navigate four levels up to reach the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Adjust sys.path if necessary for Streamlit's execution context,
# though direct imports from whatsapp_manager should work if src is in PYTHONPATH
# or if Streamlit runs from the project root and picks up src.
# For robustness, especially if running pages directly or in some deployments:
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from whatsapp_manager.core.group_controller import GroupController
from whatsapp_manager.utils.groups_util import GroupUtils
from whatsapp_manager.utils.task_scheduler import TaskScheduled
from whatsapp_manager.core.send_sandeco import SendSandeco


# --- Light Theme CSS ---
st.set_page_config(page_title='WhatsApp Group Resumer - PT', layout='wide')

# This page is the Portuguese version of the app

# Load environment variables
env_path = os.path.join(PROJECT_ROOT, '.env')
# st.write(f"Carregando .env de: {env_path}") # Optional: for debugging
load_dotenv(env_path, override=True)


st.markdown("""
   
""", unsafe_allow_html=True)

# Initialize core components
try:
    control = GroupController()
    groups = control.fetch_groups()
    ut = GroupUtils()
    group_map, options = ut.map(groups)
    sender = SendSandeco()
    initialization_error = None
except Exception as e:
    control = None
    groups = []
    ut = None
    group_map = {}
    options = []
    sender = None
    initialization_error = str(e)

col1, col2 = st.columns([1, 1])

# Check for initialization errors
if initialization_error:
    st.error("❌ **Erro na Inicialização**")
    if "autenticação" in initialization_error.lower():
        st.error("Erro de autenticação com a API Evolution:")
        with st.expander("Detalhes do erro"):
            st.code(initialization_error)
        st.info("💡 **Verifique:**")
        st.markdown("""
        - Se o servidor Evolution API está rodando
        - Se as credenciais no arquivo .env estão corretas
        - Se a URL base está acessível
        """)
    else:
        st.error(f"Erro: {initialization_error}")
    st.stop()  # Stop execution if there's an initialization error

def load_scheduled_groups():
    csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
    try:
        df = pd.read_csv(csv_path)
        return df[df['enabled'] == True]
    except FileNotFoundError:
        st.warning(f"Arquivo group_summary.csv não encontrado em {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar grupos agendados: {e}")
        return pd.DataFrame()


def delete_scheduled_group(group_id):
    csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
    try:
        df = pd.read_csv(csv_path)
        if group_id not in df['group_id'].values:
            st.error(f"Grupo com ID {group_id} não encontrado!")
            return False
        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            st.success(f"Tarefa {task_name} removida do sistema")
        except Exception as e:
            st.warning(f"Aviso: Não foi possível remover a tarefa: {e}")
        df = df[df['group_id'] != group_id]
        df.to_csv(csv_path, index=False)
        st.success("Grupo removido do arquivo de configuração")
        return True
    except FileNotFoundError:
        st.error(f"Arquivo group_summary.csv não encontrado em {csv_path}")
        return False
    except Exception as e:
        st.error(f"Erro ao remover grupo: {e}")
        return False

with col1:
    st.header("Selecione um Grupo")
    if st.button("Atualizar Lista de Grupos"):
        if control is None:
            st.error("Sistema não inicializado corretamente. Verifique as configurações.")
            st.stop()
        with st.spinner("Atualizando grupos..."):
            try:
                # Use force_refresh=True to bypass cache
                control.fetch_groups(force_refresh=True) 
                st.success("Lista de grupos atualizada!")
                t.sleep(1) # Short pause to show message
                st.rerun()
            except Exception as e:
                if "autenticação" in str(e).lower():
                    st.error("❌ **Erro de Autenticação**")
                    st.error("Verifique suas credenciais da API Evolution no arquivo .env:")
                    with st.expander("Detalhes do erro"):
                        st.code(str(e))
                    st.info("💡 **Dicas para resolver:**")
                    st.markdown("""
                    - Verifique se o servidor Evolution API está rodando em http://192.168.1.151:8081
                    - Confirme se o EVO_API_TOKEN está correto
                    - Verifique se o EVO_INSTANCE_NAME e EVO_INSTANCE_TOKEN estão válidos
                    - Teste a conexão diretamente no navegador ou com curl
                    """)
                else:
                    st.error(f"Erro ao atualizar grupos: {str(e)}")
                    with st.expander("Detalhes do erro"):
                        st.code(str(e))

    if group_map:
        selected_group_id = st.selectbox(
            "Escolha um grupo:",
            options,
            format_func=lambda x: x[0]
        )[1]
        selected_group = group_map[selected_group_id]
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(head_group, unsafe_allow_html=True)
        ut.group_details(selected_group)
        
        st.subheader("Tarefas Agendadas")
        scheduled_groups = load_scheduled_groups()
        if not scheduled_groups.empty:
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []
            for _, row in scheduled_groups.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, "Nome não encontrado")
                if row.get('start_date') and row.get('end_date'):
                    periodicidade = "Uma vez"
                else:
                    periodicidade = "Diariamente"
                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "horario": row['horario'],
                    "links": "Sim" if row['is_links'] else "Não",
                    "names": "Sim" if row['is_names'] else "Não",
                    "periodicidade": periodicidade
                })
            options_list = [f"{info['name']} - {info['horario']}" for info in scheduled_groups_info]
            selected_idx = st.selectbox("Grupos com Resumos Agendados:", range(len(options_list)), format_func=lambda x: options_list[x])
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]
                st.write(f"ID: {selected_info['id']}")
                st.write(f"Horário: {selected_info['horario']}")
                st.write(f"Periodicidade: {selected_info['periodicidade']}")
                st.write(f"Links habilitados: {selected_info['links']}")
                st.write(f"Nomes habilitados: {selected_info['names']}")
                if st.button("Remover Agendamento"):
                    if delete_scheduled_group(selected_info['id']):
                        st.success("Agendamento removido com sucesso!")
                        st.rerun()
        else:
            st.info("Não há grupos com resumos agendados.")
    else:
        st.warning("Nenhum grupo encontrado!")

with col2:
    if group_map and 'selected_group' in locals():
        st.header("Configurações")
        with st.expander("Configurações do Resumo", expanded=True):
            enabled = st.checkbox("Habilitar Geração do Resumo", value=selected_group.enabled)
            periodicidade = st.selectbox("Periodicidade", ["Diariamente", "Uma vez"], index=0)
            horario = None
            if periodicidade == "Diariamente":
                try:
                    default_time = time.fromisoformat(selected_group.horario)
                except Exception:
                    default_time = time.fromisoformat("22:00")
                horario = st.time_input("Horário de Execução do Resumo:", value=default_time)
            start_date, end_date, start_time, end_time = None, None, None, None
            if periodicidade == "Uma vez":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input("Data de Início:", value=date.today())
                    start_time = st.time_input("Hora de Início:", value=time.fromisoformat("00:00"))
                with col_end:
                    end_date = st.date_input("Data Final:", value=date.today())
                    end_time = st.time_input("Hora Final:", value=time.fromisoformat("23:59"))
            is_links = st.checkbox("Incluir Links no Resumo", value=selected_group.is_links)
            is_names = st.checkbox("Incluir Nomes no Resumo", value=selected_group.is_names)
            send_to_group = st.checkbox("Enviar Resumo para o Grupo", value=False)
            send_to_personal = st.checkbox("Enviar Resumo para o Meu Celular", value=True)
            min_messages_summary = st.slider("Mínimo de Mensagens para Gerar Resumo:", 1, 200, 50) # Novo slider
            # Path to the summary script in core
            python_script_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")
            if st.button("Salvar Configurações"):
                task_name = f"ResumoGrupo_{selected_group.group_id}"
                try:
                    additional_params = {}
                    if periodicidade == "Uma vez":
                        additional_params.update({
                            'start_date': start_date.strftime("%Y-%m-%d"),
                            'start_time': start_time.strftime("%H:%M"),
                            'end_date': end_date.strftime("%Y-%m-%d"),
                            'end_time': end_time.strftime("%H:%M")
                        })
                    else:
                        # Limpa campos de data/hora para agendamento diário
                        additional_params.update({
                            'start_date': None,
                            'start_time': None,
                            'end_date': None,
                            'end_time': None
                        })
                    if control.update_summary(
                        group_id=selected_group.group_id,
                        horario=horario.strftime("%H:%M") if horario else None,
                        enabled=enabled,
                        is_links=is_links,
                        is_names=is_names,
                        send_to_group=send_to_group,
                        send_to_personal=send_to_personal,
                        script=python_script_path, # Use updated path
                        min_messages_summary=min_messages_summary,  # Passar o novo valor
                        **additional_params
                    ):
                        if enabled:
                            if periodicidade == "Diariamente":
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script_path, # Use updated path
                                    schedule_type='DAILY',
                                    time=horario.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado diariamente às {horario.strftime('%H:%M')}")
                            else:
                                next_minute = datetime.now().replace(second=0, microsecond=0) + pd.Timedelta(minutes=1)
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script_path, # Use updated path
                                    schedule_type='ONCE',
                                    date=next_minute.strftime("%Y-%m-%d"),
                                    time=next_minute.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado em {next_minute.strftime('%d/%m/%Y às %H:%M')}")
                        else:
                            try:
                                TaskScheduled.delete_task(task_name)
                            except Exception:
                                pass
                            st.success("Configurações salvas! Agendamento desativado.")
                        if send_to_personal:
                            pass  # Removido envio automático de mensagem ao salvar agendamento
                        t.sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar as configurações. Tente novamente!")
                except Exception as e:
                    st.error(f"Erro ao configurar agendamento: {str(e)}")
    else:
        st.warning("Nenhum grupo encontrado!")