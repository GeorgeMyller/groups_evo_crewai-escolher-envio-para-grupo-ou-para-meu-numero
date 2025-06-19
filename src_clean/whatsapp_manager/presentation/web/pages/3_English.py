import os
import time as t
from datetime import time, date, datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Import from the new clean architecture
from whatsapp_manager.core.services.group_service import GroupService
from whatsapp_manager.infrastructure.persistence.group_repository import GroupRepository
from whatsapp_manager.infrastructure.scheduling.task_scheduler import TaskSchedulingService
from whatsapp_manager.infrastructure.messaging.message_sender import MessageSender
from whatsapp_manager.shared.utils.group_utils import GroupUtilsService
from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper

# --- Page Config ---
st.set_page_config(page_title='WhatsApp Group Summarizer - EN', layout='wide')

# --- Load Environment Variables ---
load_dotenv(override=True)

# --- Core Components Initialization ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def initialize_components():
    """Initialize all necessary components from the clean architecture."""
    try:
        # Infrastructure
        repo = GroupRepository()
        
        # Load credentials from .env
        base_url = os.getenv("EVO_BASE_URL")
        api_token = os.getenv("EVO_API_TOKEN")
        instance_id = os.getenv("EVO_INSTANCE_NAME")
        instance_token = os.getenv("EVO_INSTANCE_TOKEN")

        if not all([base_url, api_token, instance_id, instance_token]):
            st.error("Missing Evolution API credentials in .env file.")
            return {
                "group_service": None, "sender": None, "ut": None, "scheduler": None,
                "groups": [], "group_map": {}, "options": [],
                "mode": "error", "error": "Missing credentials"
            }

        client = EvolutionClientWrapper(base_url, api_token, instance_id, instance_token)
        scheduler = TaskSchedulingService()
        sender = MessageSender(client)

        # Services
        group_service = GroupService(client, repo)

        # Utils
        ut = GroupUtilsService()

        # Initial data fetch
        groups = group_service.fetch_groups()
        mode = "online" if client.is_instance_connected() else "offline"
        
        if mode == "online":
            st.success("✅ **System initialized successfully**")
        else:
            st.warning("⚠️ **Offline mode active** - Using local data")

        group_map, options = ut.create_group_options_map(groups)

        return {
            "group_service": group_service,
            "sender": sender,
            "ut": ut,
            "scheduler": scheduler,
            "groups": groups,
            "group_map": group_map,
            "options": options,
            "mode": mode,
            "error": None
        }

    except Exception as e:
        st.error(f"❌ Initialization Error: {e}")
        return {
            "group_service": None, "sender": None, "ut": None, "scheduler": None,
            "groups": [], "group_map": {}, "options": [],
            "mode": "error", "error": str(e)
        }

# --- Main App ---
with st.spinner("🔄 Initializing system..."):
    components = initialize_components()

group_service = components["group_service"]
sender = components["sender"]
ut = components["ut"]
scheduler = components["scheduler"]
groups = components["groups"]
group_map = components["group_map"]
options = components["options"]
mode = components["mode"]
initialization_error = components["error"]

if initialization_error:
    st.error(f"❌ **Critical Initialization Error:** {initialization_error}")
    st.stop()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Manage Groups")

    # --- Mode and Refresh ---
    if mode == "offline":
        st.info("🔒 **Offline Mode Active**")
        if st.button("🔄 Try to Reconnect and Refresh"):
            st.cache_data.clear()
            st.rerun()
    elif mode == "online":
        if st.button("🔄 Refresh Groups from API"):
            with st.spinner("Fetching groups..."):
                group_service.fetch_groups(force_refresh=True)
                st.cache_data.clear()
                st.success("Groups updated!")
                t.sleep(1)
                st.rerun()

    # --- Group Selection ---
    if not group_map:
        st.warning("No groups found!")
        st.stop()

    selected_group_id = st.selectbox(
        "Choose a group:",
        options,
        format_func=lambda x: x[0]
    )[1]
    selected_group = group_map[selected_group_id]

    # --- Display Group Info ---
    head_group = ut.create_group_header_display(selected_group.name, selected_group.picture_url)
    st.markdown(head_group, unsafe_allow_html=True)
    ut.display_group_details(selected_group)

    # --- Scheduled Groups Management ---
    st.subheader("Scheduled Tasks")
    scheduled_groups_dict = group_service.group_repository.load_all_summary_data()
    import pandas as pd
    if scheduled_groups_dict:
        scheduled_groups = pd.DataFrame(list(scheduled_groups_dict.values()))
        group_dict = {group.group_id: group.name for group in groups}
        scheduled_groups['name'] = scheduled_groups['group_id'].map(group_dict).fillna("Name not found")

        options_list = [f"{row['name']} - {row['horario']}" for _, row in scheduled_groups.iterrows()]
        selected_idx = st.selectbox("Scheduled Summaries:", range(len(options_list)), format_func=lambda x: options_list[x])

        if selected_idx is not None:
            selected_info = scheduled_groups.iloc[selected_idx]
            st.write(f"**ID:** `{selected_info['group_id']}`")
            st.write(f"**Time:** {selected_info['horario']}")
            st.write(f"**Frequency:** {'Daily' if pd.isna(selected_info.get('start_date')) else 'Once'}")

            if st.button("Remove Schedule", key=f"del_{selected_info['group_id']}"):
                with st.spinner("Removing schedule..."):
                    try:
                        scheduler.delete_task(f"GroupSummary_{selected_info['group_id']}")
                        group_service.update_summary_settings(selected_info['group_id'], enabled=False)
                        st.success("Schedule removed successfully!")
                        t.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing schedule: {e}")
    else:
        st.info("No scheduled summaries.")

with col2:
    st.header("Summary Settings")
    with st.expander("Settings", expanded=True):
        enabled = st.checkbox("Enable Summary Generation", value=selected_group.enabled)
        frequency = st.selectbox("Frequency", ["Daily", "Once"], index=0)
        
        horario_str = selected_group.horario if selected_group.horario else "22:00"
        default_time = time.fromisoformat(horario_str)
        horario = st.time_input("Execution Time:", value=default_time)

        start_date, end_date = None, None
        if frequency == "Once":
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input("Start Date:", value=date.today())
            with col_end:
                end_date = st.date_input("End Date:", value=date.today())

        is_links = st.checkbox("Include Links", value=selected_group.is_links)
        is_names = st.checkbox("Include Names", value=selected_group.is_names)
        send_to_group = st.checkbox("Send to Group", value=False)
        send_to_personal = st.checkbox("Send to My Number", value=True)
        min_messages = st.slider("Minimum Messages to Summarize:", 1, 200, selected_group.min_messages_summary or 50)

        if st.button("Save Settings"):
            if not enabled:
                try:
                    scheduler.delete_task(f"GroupSummary_{selected_group.group_id}")
                    group_service.update_summary_settings(selected_group.group_id, enabled=False)
                    st.success("Schedule disabled and settings saved.")
                    t.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error disabling schedule: {e}")
            else:
                schedule_details = {
                    "group_id": selected_group.group_id,
                    "schedule_type": 'DAILY' if frequency == "Daily" else 'ONCE',
                    "time": horario.strftime("%H:%M"),
                    "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                    "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
                }
                summary_config = {
                    "horario": horario.strftime("%H:%M"),
                    "enabled": enabled,
                    "is_links": is_links,
                    "is_names": is_names,
                    "send_to_group": send_to_group,
                    "send_to_personal": send_to_personal,
                    "min_messages_summary": min_messages,
                }

                with st.spinner("Saving and scheduling..."):
                    try:
                        group_service.update_summary_settings(selected_group.group_id, **summary_config)
                        
                        if schedule_details['schedule_type'] == 'DAILY':
                            scheduler.create_task(
                                task_name=f"GroupSummary_{selected_group.group_id}",
                                python_script_path=os.path.join(os.getcwd(), "src_clean", "whatsapp_manager", "core", "use_cases", "run_summary.py"),
                                schedule_type='DAILY',
                                time=schedule_details['time'],
                                arguments=[selected_group.group_id]
                            )
                        else: # ONCE
                             scheduler.create_task(
                                task_name=f"GroupSummary_{selected_group.group_id}",
                                python_script_path=os.path.join(os.getcwd(), "src_clean", "whatsapp_manager", "core", "use_cases", "run_summary.py"),
                                schedule_type='ONCE',
                                date=schedule_details['start_date'],
                                time=schedule_details['time'],
                                arguments=[selected_group.group_id]
                            )
                        st.success("Settings saved and summary scheduled!")
                        t.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving settings: {e}")
