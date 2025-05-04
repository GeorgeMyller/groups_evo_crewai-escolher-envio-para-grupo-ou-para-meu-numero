import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

st.set_page_config(page_title='System Dashboard', layout='wide')
st.title("📊 System Activity Dashboard")

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'log_summary.txt')

def parse_log_line(line):
    """Parses a single log line."""
    match = re.match(r"\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] - Mensagem: (.*)", line)
    if match:
        timestamp_str, level, group_info, group_id_info, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        
        group_name_match = re.search(r"GRUPO: (.*?)$", group_info)
        group_name = group_name_match.group(1).strip() if group_name_match else "N/A"
        
        group_id_match = re.search(r"GROUP_ID: (.*?@g\.us)$", group_id_info)
        group_id = group_id_match.group(1).strip() if group_id_match else "N/A"

        send_type = "Unknown"
        if "enviado com sucesso para grupo e número pessoal" in message:
            send_type = "Group & Personal"
        elif "enviado com sucesso para número pessoal" in message:
            send_type = "Personal"
        elif "enviado com sucesso!" in message: # Assuming this means group only based on older logs
             send_type = "Group"
             
        return {
            "Timestamp": timestamp,
            "Level": level,
            "Group Name": group_name,
            "Group ID": group_id,
            "Send Type": send_type,
            "Message": message
        }
    return None

def load_log_data(log_file):
    """Loads and parses the log file."""
    logs = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                parsed_line = parse_log_line(line.strip())
                if parsed_line:
                    logs.append(parsed_line)
    except FileNotFoundError:
        st.error(f"Log file not found at: {log_file}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading log file: {e}")
        return pd.DataFrame()
        
    if not logs:
        st.warning("No log entries found or failed to parse.")
        return pd.DataFrame()
        
    df = pd.DataFrame(logs)
    df = df.sort_values(by="Timestamp", ascending=False)
    return df

log_df = load_log_data(LOG_FILE_PATH)

if not log_df.empty:
    st.header("Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    total_summaries = len(log_df)
    col1.metric("Total Summaries Generated", total_summaries)
    
    unique_groups = log_df['Group Name'].nunique()
    col2.metric("Unique Groups Processed", unique_groups)

    send_type_counts = log_df['Send Type'].value_counts()
    col3.metric("Most Common Send Type", send_type_counts.index[0] if not send_type_counts.empty else "N/A", f"{send_type_counts.iloc[0] if not send_type_counts.empty else 0} times")

    st.header("Summaries per Group")
    group_counts = log_df['Group Name'].value_counts()
    st.bar_chart(group_counts)

    st.header("Send Destination Distribution")
    st.bar_chart(send_type_counts)

    st.header("Latest Activity")
    st.dataframe(log_df.head(10)) # Display the 10 most recent log entries
else:
    st.info("No log data available to display.")

# Note: summary_execution.log was found to be empty and is not included here.
