import streamlit as st
import os
import pandas as pd
from datetime import time, date, datetime, timedelta
import time as t # Renamed to avoid conflict
from dotenv import load_dotenv

# Set page config first
st.set_page_config(page_title='Group Management and Scheduling (EN)', layout='wide')

# Load environment variables relative to the main app.py directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# st.write(f"Loading .env from: {env_path}") # Commented out to keep UI clean
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
    """Load enabled scheduled groups from CSV."""
    try:
        df = pd.read_csv(CSV_PATH)
        return df[df['enabled'] == True]
    except FileNotFoundError:
        # Create the file with headers if it doesn't exist
        pd.DataFrame(columns=['group_id', 'horario', 'enabled', 'is_links', 'is_names', 'send_to_group', 'send_to_personal', 'script', 'start_date', 'end_date', 'start_time', 'end_time']).to_csv(CSV_PATH, index=False)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading schedules: {e}")
        return pd.DataFrame()

def delete_scheduled_group(group_id):
    """Remove a scheduled group from CSV and system tasks."""
    try:
        df = pd.read_csv(CSV_PATH)
        if group_id not in df['group_id'].values:
            st.error(f"Group ID {group_id} not found in CSV!")
            return False

        task_name = f"ResumoGrupo_{group_id}" # Use consistent task naming
        try:
            TaskScheduled.delete_task(task_name)
            st.success(f"Task {task_name} removed from system.")
        except Exception as e:
            # Don't stop the process if task deletion fails
            st.warning(f"Warning: Could not remove scheduled task '{task_name}' (it might have been removed already or never existed): {e}")

        df = df[df['group_id'] != group_id]
        df.to_csv(CSV_PATH, index=False)
        st.success(f"Schedule for group {group_id} removed from configuration file.")
        return True
    except FileNotFoundError:
        st.error("File group_summary.csv not found.")
        return False
    except Exception as e:
        st.error(f"Error removing schedule for group {group_id}: {e}")
        return False

# --- Streamlit UI --- 

st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Group Management & Scheduling</h1>', unsafe_allow_html=True)

# Button to manually refresh groups in the sidebar
if st.sidebar.button('Refresh Group List'):
    with st.spinner('Refreshing groups...'):
        # Pass cache path to controller
        control.fetch_groups(force_refresh=True)
    st.sidebar.success('Groups refreshed successfully!')
    st.rerun() # Rerun to reflect changes

# Load group list (uses cache by default or refreshed list)
groups = control.fetch_groups()
group_map, options = ut.map(groups)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Select a Group")
    if group_map:
        # Dropdown to select a group
        selected_option = st.selectbox(
            "Choose a group:",
            options,
            format_func=lambda x: x[0], # Show only name in dropdown
            key="en_group_select" # Unique key for this widget
        )
        selected_group_id = selected_option[1] # Get ID from selected option
        selected_group = group_map[selected_group_id]

        # Display selected group details
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(f'<div class="group-details">{head_group}</div>', unsafe_allow_html=True)
        with st.expander("Group Details", expanded=False):
            ut.group_details(selected_group)

        # Scheduled Tasks Section
        st.subheader("Active Scheduled Tasks")
        scheduled_groups_df = load_scheduled_groups()

        if not scheduled_groups_df.empty:
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []

            for _, row in scheduled_groups_df.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, f"ID: {group_id}") # Fallback to ID if name not found
                horario = row.get('horario', 'N/A')
                start_date_str = row.get('start_date')
                end_date_str = row.get('end_date')
                start_time_str = row.get('start_time')
                end_time_str = row.get('end_time')

                # Determine frequency based on filled fields
                if horario and not start_date_str:
                    frequency = f"Daily at {horario}"
                elif start_date_str and start_time_str:
                    frequency = f"Once on {start_date_str} at {start_time_str}"
                else:
                    frequency = "Undefined"

                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "time_or_date": horario if horario and not start_date_str else f"{start_date_str} {start_time_str}",
                    "frequency": frequency,
                    "display_text": f"{group_name} - {frequency}"
                })

            # Dropdown to select a scheduled task
            options_list = [info['display_text'] for info in scheduled_groups_info]
            if options_list:
                selected_task_idx = st.selectbox("Groups with Scheduled Summaries:",
                                               range(len(options_list)),
                                               format_func=lambda x: options_list[x],
                                               key="en_scheduled_select")

                if selected_task_idx is not None:
                    selected_info = scheduled_groups_info[selected_task_idx]
                    st.write(f"**Group:** {selected_info['name']}")
                    st.write(f"**ID:** {selected_info['id']}")
                    st.write(f"**Schedule:** {selected_info['frequency']}")

                    # Button to remove the schedule
                    if st.button("Remove Schedule", key=f"remove_en_{selected_info['id']}", type="secondary"):
                        if delete_scheduled_group(selected_info['id']):
                            st.success(f"Schedule for {selected_info['name']} removed.")
                            t.sleep(1) # Brief pause for user to see message
                            st.rerun()
                        else:
                            st.error("Failed to remove schedule.")
            else:
                st.info("No active scheduled summaries found.")
        else:
            st.info("No active scheduled summaries found.")
    else:
        st.warning("No groups found! Try refreshing the list.")

with col2:
    if group_map and selected_group: # Ensure a group is selected
        st.header("Summary Settings")
        with st.expander("Adjust Schedule and Options", expanded=True):

            # Load saved config for the selected group, if it exists
            saved_config_df = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()
            group_config = saved_config_df[saved_config_df['group_id'] == selected_group_id]
            current_config = group_config.iloc[0].to_dict() if not group_config.empty else {}

            # --- Configuration Form ---
            enabled = st.checkbox("Enable Summary Generation",
                                value=current_config.get('enabled', False), # Default to False if not configured
                                key=f"en_enable_{selected_group_id}")

            frequency = st.selectbox("Frequency",
                                     ["Daily", "Once"],
                                     index=0 if not current_config.get('start_date') else 1,
                                     key=f"en_freq_{selected_group_id}")

            summary_time = None # Renamed from horario
            start_date, end_date, start_time, end_time = None, None, None, None

            if frequency == "Daily":
                default_time_str = current_config.get('horario', "09:00") # Use 'horario' from CSV
                try:
                    default_time = datetime.strptime(default_time_str, "%H:%M").time()
                except (ValueError, TypeError):
                    default_time = time(9, 0) # Fallback
                summary_time = st.time_input("Daily Execution Time:",
                                           value=default_time,
                                           key=f"en_time_{selected_group_id}")
            else: # Frequency == "Once"
                col_start, col_end = st.columns(2)
                with col_start:
                    default_start_date_str = current_config.get('start_date', date.today().strftime('%Y-%m-%d'))
                    try:
                        default_start_date = datetime.strptime(default_start_date_str, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        default_start_date = date.today()
                    # Ensure default date is never less than min_value
                    if default_start_date < date.today():
                        default_start_date = date.today()
                    start_date = st.date_input("Start Date:",
                                             value=default_start_date,
                                             min_value=date.today(),
                                             key=f"en_start_date_{selected_group_id}")
                    
                    default_start_time_str = current_config.get('start_time', (datetime.now() + timedelta(minutes=5)).strftime('%H:%M'))
                    try:
                        default_start_time = datetime.strptime(default_start_time_str, '%H:%M').time()
                    except (ValueError, TypeError):
                        default_start_time = (datetime.now() + timedelta(minutes=5)).time()
                    start_time = st.time_input("Start Time:",
                                             value=default_start_time,
                                             key=f"en_start_time_{selected_group_id}")
                # End Date/Time fields (optional, not currently used for "Once")
                # with col_end:
                #     end_date = st.date_input("End Date:", value=start_date + timedelta(days=1), min_value=start_date)
                #     end_time = st.time_input("End Time:", value=time(23, 59))

            is_links = st.checkbox("Include Links in Summary",
                                 value=current_config.get('is_links', True),
                                 key=f"en_links_{selected_group_id}")
            is_names = st.checkbox("Include Names in Summary",
                                 value=current_config.get('is_names', True),
                                 key=f"en_names_{selected_group_id}")

            send_to_group = st.checkbox("Send Summary to Group",
                                      value=current_config.get('send_to_group', True),
                                      key=f"en_send_group_{selected_group_id}")
            send_to_personal = st.checkbox("Send Summary to My Phone",
                                         value=current_config.get('send_to_personal', False),
                                         key=f"en_send_personal_{selected_group_id}")

            # Save Settings Button
            if st.button("Save Settings", key=f"save_en_{selected_group_id}"):
                task_name = f"ResumoGrupo_{selected_group.group_id}" # Consistent task name
                config_data = {
                    'group_id': selected_group.group_id,
                    'enabled': enabled,
                    'is_links': is_links,
                    'is_names': is_names,
                    'send_to_group': send_to_group,
                    'send_to_personal': send_to_personal,
                    'script': PYTHON_SCRIPT_PATH,
                    'horario': summary_time.strftime("%H:%M") if summary_time else None,
                    'start_date': start_date.strftime("%Y-%m-%d") if start_date else None,
                    'end_date': end_date.strftime("%Y-%m-%d") if end_date else None,
                    'start_time': start_time.strftime("%H:%M") if start_time else None,
                    'end_time': end_time.strftime("%H:%M") if end_time else None
                }

                try:
                    # Update or add the configuration in the CSV
                    if os.path.exists(CSV_PATH):
                        df = pd.read_csv(CSV_PATH)
                    else:
                        df = pd.DataFrame(columns=config_data.keys())

                    if selected_group.group_id in df['group_id'].values:
                        # Update existing row
                        idx = df.index[df['group_id'] == selected_group.group_id].tolist()[0]
                        for key, value in config_data.items():
                            df.loc[idx, key] = value
                    else:
                        # Add new row
                        new_row = pd.DataFrame([config_data])
                        df = pd.concat([df, new_row], ignore_index=True)

                    df.to_csv(CSV_PATH, index=False)
                    st.success("Settings saved to CSV file!")

                    # Manage the scheduled task
                    if enabled:
                        if frequency == "Daily" and summary_time:
                            TaskScheduled.create_task(
                                task_name=task_name,
                                python_script_path=PYTHON_SCRIPT_PATH,
                                schedule_type='DAILY',
                                time=summary_time.strftime("%H:%M")
                            )
                            st.success(f"Daily schedule set for {summary_time.strftime('%H:%M')}!")
                        elif frequency == "Once" and start_date and start_time:
                            # Combine date and time
                            run_datetime = datetime.combine(start_date, start_time)
                            now = datetime.now()
                            if run_datetime <= now:
                                st.error("The selected date and time for the single run has already passed. Please choose a future time.")
                            else:
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=PYTHON_SCRIPT_PATH,
                                    schedule_type='ONCE',
                                    date=start_date.strftime("%Y-%m-%d"),
                                    time=start_time.strftime("%H:%M")
                                )
                                st.success(f"One-time schedule set for {start_date.strftime('%Y-%m-%d')} at {start_time.strftime('%H:%M')}!")
                        else:
                            st.warning("Incomplete schedule configuration (check time/date).")
                    else: # If not enabled, try to remove existing task
                        try:
                            TaskScheduled.delete_task(task_name)
                            st.info("Schedule disabled and task removed (if it existed).")
                        except Exception:
                            st.info("Schedule disabled (no existing task found to remove).")
                            pass # Not an error if task doesn't exist

                    # Optional: Immediate send for testing (can be removed)
                    # if send_to_personal:
                    #     personal_number = os.getenv('WHATSAPP_NUMBER')
                    #     if personal_number:
                    #         try:
                    #             sender.textMessage(number=personal_number, msg=f"Test: Settings saved for group {selected_group.name}.")
                    #             st.success("Test message sent to your phone!")
                    #         except Exception as send_err:
                    #             st.error(f"Error sending test message: {send_err}")
                    #     else:
                    #         st.error("Personal number (WHATSAPP_NUMBER) not configured in .env for test send.")

                    t.sleep(1) # Pause for user to read
                    st.rerun()

                except Exception as e:
                    st.error(f"Error saving settings or scheduling task: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc()) # Show more error details

    else:
        st.info("Select a group in the left column to view settings.")

# Close the main wrapper
st.markdown('</div>', unsafe_allow_html=True)
