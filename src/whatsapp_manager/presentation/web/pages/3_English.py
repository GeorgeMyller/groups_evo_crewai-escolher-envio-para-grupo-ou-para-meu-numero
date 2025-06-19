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
# Define Project Root. This file is in src/whatsapp_manager/presentation/web/pages/
# Navigate five levels up to reach the project root /app/.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

# Add src to Python path for imports, if not already there
# This allows imports like `from whatsapp_manager.core...`
import sys
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import local modules
from whatsapp_manager.core.controllers.group_controller import GroupController
from whatsapp_manager.shared.utils.group_utils import GroupUtilsService
from whatsapp_manager.infrastructure.scheduling.task_scheduler import TaskSchedulingService
# SendSandeco import removed


# --- Page Setup ---
st.set_page_config(page_title='WhatsApp Group Resumer - EN', layout='wide')

# This page is the English version of the app

# Load environment variables
env_path = os.path.join(PROJECT_ROOT, '.env')
# st.write(f"Loading .env from: {env_path}") # Optional: for debugging
load_dotenv(env_path, override=True)


st.markdown("""

""", unsafe_allow_html=True)

# Initialize core components
@st.cache_data(ttl=300)  # Cache for 5 minutes
def initialize_components():
    """Initialize GroupController with proper error handling and fallback modes."""
    try:
        # Initialize GroupController
        control = GroupController()
        
        # Simple status check by trying to fetch groups
        try:
            groups = control.fetch_groups()
            mode = "online"
            st.success("✅ **System initialized successfully**")
        except Exception as e:
            # Try to get groups from cache/local data
            try:
                groups = control.get_groups()  # Try to get cached groups
                mode = "offline" 
                st.warning("⚠️ **Offline mode active** - Using local data")
            except Exception:
                groups = []
                mode = "offline"
                st.warning("⚠️ **No data available** - Check connectivity")
            
        ut = GroupUtilsService() # Updated to GroupUtilsService
        group_map, options = ut.create_group_options_map(groups) # Updated method call
        # sender = SendSandeco() # Removed SendSandeco instantiation
        
        return {
            "control": control,
            "groups": groups,
            "ut": ut,
            "group_map": group_map,
            "options": options,
            # "sender": sender, # Removed sender from return
            "mode": mode,
            "error": None
        }
        
    except Exception as e:
        return {
            "control": None,
            "groups": [],
            "ut": None,
            "group_map": {},
            "options": [],
            "sender": None,
            "mode": "error",
            "error": str(e)
        }

# Initialize components
with st.spinner("🔄 Initializing system..."):
    components = initialize_components()

control = components["control"]
groups = components["groups"]
ut = components["ut"]
group_map = components["group_map"]
options = components["options"]
sender = components["sender"]
mode = components["mode"]
initialization_error = components["error"]

col1, col2 = st.columns([1, 1])

# Check for initialization errors or provide mode information
if initialization_error:
    st.error("❌ **Initialization Error**")
    if "authentication" in initialization_error.lower() or "autenticação" in initialization_error.lower(): # Check for auth error in PT too
        st.error("Authentication error with the Evolution API:")
        with st.expander("Error details"):
            st.code(initialization_error)
        st.info("💡 **Please check:**")
        st.markdown("""
        - If the Evolution API server is running.
        - If the credentials in the .env file are correct.
        - If the base URL is accessible.
        """)
    else:
        st.error(f"Error: {initialization_error}")
    st.stop()

# Show mode information
if mode == "offline":
    st.info("🔒 **Offline Mode Active** - Working with locally saved data")
    if st.button("🔄 Try Reconnect API"):
        st.cache_data.clear()
        st.rerun()
elif mode == "online":
    if st.button("🔄 Refresh Groups from API"):
        st.cache_data.clear()
        st.rerun()


def load_scheduled_groups():
    csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
    try:
        df = pd.read_csv(csv_path)
        return df[df['enabled'] == True]
    except FileNotFoundError:
        st.warning(f"group_summary.csv not found at {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading scheduled groups: {e}")
        return pd.DataFrame()


def delete_scheduled_group(group_id):
    csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
    try:
        df = pd.read_csv(csv_path)
        if group_id not in df['group_id'].values:
            st.error(f"Group ID {group_id} not found!")
            return False
        task_name = f"GroupSummary_{group_id}" # Task name in English version
        try:
            TaskSchedulingService().remove_task(task_name) # Instantiate and call
            st.success(f"Task {task_name} removed from system")
        except Exception as e:
            st.warning(f"Warning: Could not remove task: {e}")
        df = df[df['group_id'] != group_id]
        df.to_csv(csv_path, index=False)
        st.success("Group removed from configuration file")
        return True
    except FileNotFoundError:
        st.error(f"group_summary.csv not found at {csv_path}")
        return False
    except Exception as e:
        st.error(f"Error removing group: {e}")
        return False

with col1:
    st.header("Select a Group")
    if st.button("Refresh Group List"):
        if control is None: # Added check for control
            st.error("System not initialized correctly. Check settings.")
            st.stop()
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
                    - Check if Evolution API server is running (e.g., at http://localhost:8081 or your configured URL)
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
        # Updated method calls for GroupUtilsService
        head_group_html = ut.create_group_header_display(selected_group.name, selected_group.picture_url)
        st.markdown(head_group_html, unsafe_allow_html=True)
        ut.display_group_details(selected_group)

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
                    "time": row['horario'], # Assuming 'horario' is the column name for time
                    "links": "Yes" if row.get('is_links', False) else "No", # Added .get for safety
                    "names": "Yes" if row.get('is_names', False) else "No", # Added .get for safety
                    "frequency": frequency
                })
            options_list = [f"{info['name']} - {info['time']}" for info in scheduled_groups_info]
            # Ensure options_list is not empty before creating selectbox
            if options_list:
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
                st.info("No groups with scheduled summaries found in the expected format.")
        else:
            st.info("No groups with scheduled summaries.")
    else:
        st.warning("No groups found or system not initialized!")

with col2:
    if group_map and 'selected_group' in locals() and ut is not None: # Added check for ut
        st.header("Settings")
        with st.expander("Summary Settings", expanded=True):
            enabled = st.checkbox("Enable Summary Generation", value=selected_group.enabled)
            frequency = st.selectbox("Frequency", ["Daily", "Once"], index=0)
            summary_time_val = None # Renamed to avoid conflict with datetime.time
            if frequency == "Daily":
                try:
                    default_time_val = time.fromisoformat(selected_group.horario)
                except (TypeError, ValueError): # More specific exceptions
                    default_time_val = time.fromisoformat("22:00")
                summary_time_val = st.time_input("Summary Execution Time:", value=default_time_val)

            start_date_val, end_date_val, start_time_val, end_time_val = None, None, None, None # Renamed
            if frequency == "Once":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date_val = st.date_input("Start Date:", value=date.today())
                    start_time_val = st.time_input("Start Time:", value=time.fromisoformat("00:00"))
                with col_end:
                    end_date_val = st.date_input("End Date:", value=date.today())
                    end_time_val = st.time_input("End Time:", value=time.fromisoformat("23:59"))

            is_links = st.checkbox("Include Links in Summary", value=selected_group.is_links)
            is_names = st.checkbox("Include Names in Summary", value=selected_group.is_names)
            send_to_group = st.checkbox("Send Summary to Group", value=False)
            send_to_personal = st.checkbox("Send Summary to My Phone", value=True)
            min_messages_summary = st.slider("Minimum Messages to Generate Summary:", 1, 200, getattr(selected_group, 'min_messages_summary', 50))


            python_script_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")
            if st.button("Save Settings"):
                if control is None: # Added check
                    st.error("System not initialized. Cannot save settings.")
                    st.stop()

                task_name = f"GroupSummary_{selected_group.group_id}" # Task name in English
                try:
                    additional_params = {}
                    if frequency == "Once":
                        additional_params.update({
                            'start_date': start_date_val.strftime("%Y-%m-%d") if start_date_val else None,
                            'start_time': start_time_val.strftime("%H:%M") if start_time_val else None,
                            'end_date': end_date_val.strftime("%Y-%m-%d") if end_date_val else None,
                            'end_time': end_time_val.strftime("%H:%M") if end_time_val else None
                        })
                    else:
                        additional_params.update({
                            'start_date': None,
                            'start_time': None,
                            'end_date': None,
                            'end_time': None
                        })

                    # Ensure min_messages_summary is passed to update_summary
                    # The original code was missing this in the English version
                    # Corrected method call to update_group_summary_settings
                    update_result = control.update_group_summary_settings(
                        group_id=selected_group.group_id,
                        horario=summary_time_val.strftime("%H:%M") if summary_time_val else None,
                        enabled=enabled,
                        is_links=is_links,
                        is_names=is_names,
                        send_to_group=send_to_group,
                        send_to_personal=send_to_personal,
                        # script=python_script_path, # script param not in update_group_summary_settings
                        min_messages_summary=min_messages_summary,
                        **additional_params
                    )

                    if update_result:
                        if enabled:
                            scheduler = TaskSchedulingService() # Instantiate the service
                            if frequency == "Daily" and summary_time_val:
                                scheduler.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script_path,
                                    schedule_type='DAILY',
                                    time=summary_time_val.strftime("%H:%M")
                                )
                                st.success(f"Settings saved! Summary will run daily at {summary_time_val.strftime('%H:%M')}")
                            elif frequency == "Once":
                                if start_date_val and start_time_val:
                                    scheduler.create_task(
                                        task_name=task_name,
                                        python_script_path=python_script_path,
                                        schedule_type='ONCE',
                                        date=start_date_val.strftime("%Y-%m-%d"),
                                        time=start_time_val.strftime("%H:%M")
                                    )
                                    st.success(f"Settings saved! Summary scheduled for {start_date_val.strftime('%d/%m/%Y')} at {start_time_val.strftime('%H:%M')}")
                                else:
                                    st.error("Start date and time must be set for 'Once' schedule.")
                            else:
                                st.warning("Invalid scheduling configuration.")
                except Exception as e:
                    st.error(f"Error configuring schedule: {str(e)}")
                    st.exception(e) # Show full traceback for debugging
    elif not group_map and ut is not None: # if group_map is empty but ut is initialized
        st.warning("No groups found or system not initialized correctly!")
    else:
        st.warning("No groups found!")

[end of src/whatsapp_manager/presentation/web/pages/3_English.py]
