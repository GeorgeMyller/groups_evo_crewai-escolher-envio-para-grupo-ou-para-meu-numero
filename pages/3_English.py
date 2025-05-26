import os
import streamlit as st
from datetime import time, date, datetime
import time as t
import pandas as pd
from dotenv import load_dotenv

# --- Light Theme CSS ---
st.set_page_config(page_title='WhatsApp Group Resumer - EN', layout='wide')

# This page is the English version of the app

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
st.write(f"Loading .env from: {env_path}")
load_dotenv(env_path)

from group_controller import GroupController
from groups_util import GroupUtils
from task_scheduler import TaskScheduled
from send_sandeco import SendSandeco

st.markdown("""
    
""", unsafe_allow_html=True)

# Initialize core components
control = GroupController()
groups = control.fetch_groups()
ut = GroupUtils()
group_map, options = ut.map(groups)

sender = SendSandeco()

col1, col2 = st.columns([1, 1])

def load_scheduled_groups():
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'group_summary.csv'))
        return df[df['enabled'] == True]
    except Exception:
        return pd.DataFrame()


def delete_scheduled_group(group_id):
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'group_summary.csv'))
        if group_id not in df['group_id'].values:
            st.error(f"Group ID {group_id} not found!")
            return False
        task_name = f"GroupSummary_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            st.success(f"Task {task_name} removed from system")
        except Exception as e:
            st.warning(f"Warning: Could not remove task: {e}")
        df = df[df['group_id'] != group_id]
        df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'group_summary.csv'), index=False)
        st.success("Group removed from configuration file")
        return True
    except Exception as e:
        st.error(f"Error removing group: {e}")
        return False

with col1:
    st.header("Select a Group")
    if st.button("Refresh Group List"):
        with st.spinner("Refreshing groups..."):
            try:
                 # Use force_refresh=True to bypass cache
                control.fetch_groups(force_refresh=True)
                st.success("Group list updated!")
                t.sleep(1) # Short pause to show message
                st.rerun()
            except Exception as e:
                if "autenticação" in str(e).lower() or "authentication" in str(e).lower():
                    st.error("❌ **Authentication Error**")
                    st.error("Please check your Evolution API credentials in the .env file:")
                    with st.expander("Error details"):
                        st.code(str(e))
                    st.info("💡 **Tips to resolve:**")
                    st.markdown("""
                    - Check if Evolution API server is running at http://192.168.1.151:8081
                    - Verify that EVO_API_TOKEN is correct
                    - Ensure EVO_INSTANCE_NAME and EVO_INSTANCE_TOKEN are valid
                    - Test the connection directly in browser or with curl
                    """)
                else:
                    st.error(f"Error updating groups: {str(e)}")
                    with st.expander("Error details"):
                        st.code(str(e))

    if group_map:
        selected_group_id = st.selectbox(
            "Choose a group:",
            options,
            format_func=lambda x: x[0]
        )[1]
        selected_group = group_map[selected_group_id]
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(head_group, unsafe_allow_html=True)
        ut.group_details(selected_group)
        
        st.subheader("Scheduled Tasks")
        scheduled_groups = load_scheduled_groups()
        if not scheduled_groups.empty:
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []
            for _, row in scheduled_groups.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, "Name not found")
                if row.get('start_date') and row.get('end_date'):
                    frequency = "Once"
                else:
                    frequency = "Daily"
                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "time": row['horario'],
                    "links": "Yes" if row['is_links'] else "No",
                    "names": "Yes" if row['is_names'] else "No",
                    "frequency": frequency
                })
            options_list = [f"{info['name']} - {info['time']}" for info in scheduled_groups_info]
            selected_idx = st.selectbox("Groups with Scheduled Summaries:", range(len(options_list)), format_func=lambda x: options_list[x])
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]
                st.write(f"ID: {selected_info['id']}")
                st.write(f"Time: {selected_info['time']}")
                st.write(f"Frequency: {selected_info['frequency']}")
                st.write(f"Links enabled: {selected_info['links']}")
                st.write(f"Names enabled: {selected_info['names']}")
                if st.button("Remove Schedule"):
                    if delete_scheduled_group(selected_info['id']):
                        st.success("Schedule removed successfully!")
                        st.rerun()
        else:
            st.info("No groups with scheduled summaries.")
    else:
        st.warning("No groups found!")

with col2:
    if group_map and 'selected_group' in locals():
        st.header("Settings")
        with st.expander("Summary Settings", expanded=True):
            enabled = st.checkbox("Enable Summary Generation", value=selected_group.enabled)
            frequency = st.selectbox("Frequency", ["Daily", "Once"], index=0)
            summary_time = None
            if frequency == "Daily":
                try:
                    default_time = time.fromisoformat(selected_group.horario)
                except Exception:
                    default_time = time.fromisoformat("22:00")
                summary_time = st.time_input("Summary Execution Time:", value=default_time)
            start_date, end_date, start_time, end_time = None, None, None, None
            if frequency == "Once":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input("Start Date:", value=date.today())
                    start_time = st.time_input("Start Time:", value=time.fromisoformat("00:00"))
                with col_end:
                    end_date = st.date_input("End Date:", value=date.today())
                    end_time = st.time_input("End Time:", value=time.fromisoformat("23:59"))
            is_links = st.checkbox("Include Links in Summary", value=selected_group.is_links)
            is_names = st.checkbox("Include Names in Summary", value=selected_group.is_names)
            send_to_group = st.checkbox("Send Summary to Group", value=False)
            send_to_personal = st.checkbox("Send Summary to My Phone", value=True)
            python_script = os.path.join(os.path.dirname(__file__), '..', 'summary.py')
            if st.button("Save Settings"):
                task_name = f"GroupSummary_{selected_group.group_id}"
                try:
                    additional_params = {}
                    if frequency == "Once":
                        additional_params.update({
                            'start_date': start_date.strftime("%Y-%m-%d"),
                            'start_time': start_time.strftime("%H:%M"),
                            'end_date': end_date.strftime("%Y-%m-%d"),
                            'end_time': end_time.strftime("%H:%M")
                        })
                    else:
                        # Clear date/time fields for daily scheduling
                        additional_params.update({
                            'start_date': None,
                            'start_time': None,
                            'end_date': None,
                            'end_time': None
                        })
                    if control.update_summary(
                        group_id=selected_group.group_id,
                        horario=summary_time.strftime("%H:%M") if summary_time else None,
                        enabled=enabled,
                        is_links=is_links,
                        is_names=is_names,
                        send_to_group=send_to_group,
                        send_to_personal=send_to_personal,
                        script=python_script,
                        **additional_params
                    ):
                        if enabled:
                            if frequency == "Daily":
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='DAILY',
                                    time=summary_time.strftime("%H:%M")
                                )
                                st.success(f"Settings saved! Summary will run daily at {summary_time.strftime('%H:%M')}")
                            else:
                                next_minute = datetime.now().replace(second=0, microsecond=0) + pd.Timedelta(minutes=1)
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='ONCE',
                                    date=next_minute.strftime("%Y-%m-%d"),
                                    time=next_minute.strftime("%H:%M")
                                )
                                st.success(f"Settings saved! Summary scheduled for {next_minute.strftime('%d/%m/%Y at %H:%M')}")
                        else:
                            try:
                                TaskScheduled.delete_task(task_name)
                            except Exception:
                                pass
                            st.success("Settings saved! Scheduling disabled.")
                        if send_to_personal:
                            pass  # Removido envio automático de mensagem ao salvar agendamento
                        t.sleep(2)
                        st.rerun()
                    else:
                        st.error("Error saving settings. Please try again!")
                except Exception as e:
                    st.error(f"Error configuring schedule: {str(e)}")
    else:
        st.warning("No groups found!")
