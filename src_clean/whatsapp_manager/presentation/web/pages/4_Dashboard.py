
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# Import from the new clean architecture
from src_clean.whatsapp_manager.core.services.log_service import LogService
from src_clean.whatsapp_manager.infrastructure.persistence.log_repository import LogRepository

# --- Page Config ---
st.set_page_config(
    page_title='WhatsApp Summary Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
)

# --- Custom CSS ---
st.markdown("""
<style>
.main-header { font-size: 2.5rem; color: #075E54; text-align: center; margin-bottom: 1rem; }
.metric-card { background-color: #f5f5f5; border-radius: 10px; padding: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
.chart-container { background-color: white; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📊 WhatsApp Group Summary Analytics Dashboard</h1>', unsafe_allow_html=True)

# --- Service Initialization ---
@st.cache_data(ttl=300)
def initialize_log_service():
    """Initializes the LogService."""
    try:
        repo = LogRepository()  # Assumes default log path
        service = LogService(repo)
        return service
    except Exception as e:
        st.error(f"Error initializing Log Service: {e}")
        return None

log_service = initialize_log_service()

if not log_service:
    st.stop()

# --- Data Loading ---
@st.cache_data(ttl=300)
def load_data(service):
    """Loads log data using the LogService."""
    df = service.get_log_data()
    if df.empty:
        st.warning("No log data found or failed to parse.")
    return df

log_df = load_data(log_service)

if log_df.empty:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("📊 Data Filters")

min_date = log_df['Date'].min().date()
max_date = log_df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Filter by Period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = log_df[(log_df['Date'] >= start_date) & (log_df['Date'] <= end_date)]
else:
    filtered_df = log_df

all_groups = ["All"] + sorted(filtered_df['Group Name'].unique().tolist())
selected_group = st.sidebar.selectbox("Filter by Group", all_groups)
if selected_group != "All":
    filtered_df = filtered_df[filtered_df['Group Name'] == selected_group]

send_types = ["All"] + sorted(filtered_df['Send Type'].unique().tolist())
selected_send_type = st.sidebar.selectbox("Filter by Send Type", send_types)
if selected_send_type != "All":
    filtered_df = filtered_df[filtered_df['Send Type'] == selected_send_type]

# --- Main Content ---
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Group Analysis", "⏰ Time Analysis"])

with tab1:
    st.header("📊 Key Metrics")
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Summaries", len(filtered_df))
        col2.metric("Unique Groups", filtered_df['Group Name'].nunique())
        success_rate = (filtered_df['Success'].sum() / len(filtered_df) * 100)
        col3.metric("Success Rate", f"{success_rate:.1f}%")
        most_active_group = filtered_df['Group Name'].value_counts().idxmax()
        col4.metric("Most Active Group", most_active_group)

        st.subheader("📅 Activity Timeline")
        timeline_data = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index(name='Count')
        fig = px.line(timeline_data, x='Date', y='Count', markers=True, title='Summaries per Day')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab2:
    st.header("🔄 Summaries by Group")
    if not filtered_df.empty:
        group_counts = filtered_df['Group Name'].value_counts().reset_index()
        group_counts.columns = ['Group', 'Count']
        fig = px.bar(group_counts, x='Group', y='Count', title='Total Summaries per Group', color='Count', text='Count')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📤 Distribution by Send Type")
        send_counts = filtered_df['Send Type'].value_counts().reset_index()
        send_counts.columns = ['Type', 'Count']
        fig_pie = px.pie(send_counts, values='Count', names='Type', title='Distribution by Send Type', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available for group analysis with the selected filters.")

with tab3:
    st.header("⏰ Activity Patterns")
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Activity by Day of the Week")
            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_counts = filtered_df['Day of Week'].value_counts().reindex(dow_order).fillna(0)
            st.bar_chart(dow_counts)

        with col2:
            st.subheader("Activity by Hour of the Day")
            hour_counts = filtered_df['Hour'].value_counts().sort_index()
            st.bar_chart(hour_counts)

        st.subheader("Activity Heatmap: Day of Week vs. Hour")
        day_hour_pivot = pd.pivot_table(filtered_df, values='Success', index='Day of Week', columns='Hour', aggfunc='count', fill_value=0)
        day_hour_pivot = day_hour_pivot.reindex(dow_order)
        fig_heatmap = px.imshow(day_hour_pivot, labels=dict(x="Hour of Day", y="Day of Week", color="Summaries"),
                                x=day_hour_pivot.columns, y=day_hour_pivot.index, title="Activity Heatmap")
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No data available for time analysis with the selected filters.")

# --- Detailed Data View ---
st.header("🔍 Detailed Log Data")
st.dataframe(filtered_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

