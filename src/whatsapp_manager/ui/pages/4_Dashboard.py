import calendar
from datetime import datetime
from datetime import timedelta
import os
import re

# Third-party library imports
import pandas as pd
import plotly.express as px
import streamlit as st

# Set page configuration with customized theme
st.set_page_config(
    page_title='WhatsApp Summary Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'About': "WhatsApp Group Summary Analytics Dashboard - Developed by Sandeco"
    }
)

# Add custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #075E54;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Display application header with WhatsApp-style green color
st.markdown('<h1 class="main-header">📊 WhatsApp Group Summary Analytics Dashboard</h1>', unsafe_allow_html=True)

# Define Project Root assuming this file is src/whatsapp_manager/ui/pages/4_Dashboard.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "log_summary.txt")

def parse_log_entries(log_content):
    """
    Parses the log content which may contain multiple entries per line.
    Splits each line into individual log entries and parses them.
    """
    log_entries = []
    
    # First, try to split multiple entries that might be on a single line
    # We know each entry starts with a timestamp pattern like [YYYY-MM-DD HH:MM:SS.ffffff]
    entry_pattern = r"(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\].*?)(?=\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\]|$)"
    
    for line in log_content.strip().split('\n'):
        if line.startswith('//'):  # Skip comment lines
            continue
            
        entries = re.findall(entry_pattern, line)
        for entry in entries:
            parsed_entry = parse_log_line(entry.strip())
            if parsed_entry:
                log_entries.append(parsed_entry)
    
    return log_entries

def parse_log_line(line):
    """Parses a single log entry."""
    match = re.match(r"\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] - Mensagem: (.*)", line)
    if match:
        timestamp_str, level, group_info, group_id_info, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        
        group_name_match = re.search(r"GRUPO: (.*?)$", group_info)
        group_name = group_name_match.group(1).strip() if group_name_match else "N/A"
        
        group_id_match = re.search(r"GROUP_ID: (.*?@g\.us)$", group_id_info)
        group_id = group_id_match.group(1).strip() if group_id_match else "N/A"

        # Improved send type detection with more specific patterns
        send_type = "Unknown"
        if "enviado com sucesso para grupo e número pessoal" in message:
            send_type = "Group & Personal"
        elif "enviado com sucesso para número pessoal" in message:
            send_type = "Personal"
        elif "enviado com sucesso" in message: 
            send_type = "Group"
             
        # Extract message success status
        success = True if "sucesso" in message else False
        
        # Extract date components for filtering and grouping
        date = timestamp.date()
        hour = timestamp.hour
        day_of_week = timestamp.strftime('%A')
        week_number = timestamp.isocalendar()[1]
        month = timestamp.strftime('%B')
        
        return {
            "Timestamp": timestamp,
            "Date": date,
            "Hour": hour,
            "Day of Week": day_of_week,
            "Week Number": week_number,
            "Month": month,
            "Level": level,
            "Group Name": group_name,
            "Group ID": group_id,
            "Send Type": send_type,
            "Success": success,
            "Message": message
        }
    return None

def load_log_data(log_file):
    """Loads and parses the log file."""
    logs = []
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
            logs = parse_log_entries(log_content)
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
    
    # Convert date columns to proper types for filtering
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sort by timestamp in descending order (newest first)
    df = df.sort_values(by="Timestamp", ascending=False)
    return df

log_df = load_log_data(LOG_FILE_PATH)

if not log_df.empty:
    # Create tabs for different dashboard views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Group Analysis", "⏱️ Time Analysis", "🔍 Detailed Data"])
    
    # Add sidebar for filtering
    st.sidebar.header("📊 Filtros de Dados")
    
    # Date range filter
    min_date = log_df['Date'].min().date()
    max_date = log_df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Filtrar por Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        # Convert to datetime for comparison
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + timedelta(days=1)  # Include the end date
        filtered_df = log_df[(log_df['Date'] >= start_date) & (log_df['Date'] < end_date)]
    else:
        filtered_df = log_df
    
    # Group filter
    all_groups = ["Todos"] + sorted(log_df['Group Name'].unique().tolist())
    selected_group = st.sidebar.selectbox("Filtrar por Grupo", all_groups)
    
    if selected_group != "Todos":
        filtered_df = filtered_df[filtered_df['Group Name'] == selected_group]
    
    # Send type filter
    send_types = ["Todos"] + sorted(log_df['Send Type'].unique().tolist())
    selected_send_type = st.sidebar.selectbox("Filtrar por Tipo de Envio", send_types)
    
    if selected_send_type != "Todos":
        filtered_df = filtered_df[filtered_df['Send Type'] == selected_send_type]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Filtros Aplicados")
    st.sidebar.markdown(f"**Período**: {start_date.strftime('%d/%m/%Y')} a {(end_date - timedelta(days=1)).strftime('%d/%m/%Y')}")
    st.sidebar.markdown(f"**Grupo**: {selected_group}")
    st.sidebar.markdown(f"**Tipo de Envio**: {selected_send_type}")
    
    # Display stats in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Estatísticas")
    st.sidebar.metric("Total de Registros", len(filtered_df))
    st.sidebar.metric("Total de Grupos", filtered_df['Group Name'].nunique())
    
    # Calculate success rate
    if 'Success' in filtered_df.columns:
        success_rate = (filtered_df['Success'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.sidebar.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
    
    # Calculate date range stats
    if len(filtered_df) > 0:
        date_range_days = (filtered_df['Date'].max() - filtered_df['Date'].min()).days + 1
        st.sidebar.metric("Período de Atividade", f"{date_range_days} dias")

    # TAB 1 - OVERVIEW
    with tab1:
        st.header("📊 Métricas Principais")
        
        # KPI metrics in a row of 4 columns
        col1, col2, col3, col4 = st.columns(4)
        
        total_summaries = len(filtered_df)
        col1.metric("Total de Resumos", total_summaries)
        
        unique_groups = filtered_df['Group Name'].nunique()
        col2.metric("Grupos Únicos", unique_groups)

        send_type_counts = filtered_df['Send Type'].value_counts()
        most_common_send_type = send_type_counts.index[0] if not send_type_counts.empty else "N/A"
        most_common_count = send_type_counts.iloc[0] if not send_type_counts.empty else 0
        col3.metric("Tipo de Envio Mais Comum", most_common_send_type, f"{most_common_count} vezes")
        
        # Most active group
        if not filtered_df.empty:
            group_counts = filtered_df['Group Name'].value_counts()
            most_active_group = group_counts.index[0]
            most_active_count = group_counts.iloc[0]
            col4.metric("Grupo Mais Ativo", most_active_group, f"{most_active_count} resumos")
        
        # Calculate additional metrics
        if len(filtered_df) > 0:
            # Get date range
            date_range = (filtered_df['Date'].max() - filtered_df['Date'].min()).days + 1
            avg_per_day = len(filtered_df) / date_range if date_range > 0 else 0
            
            # Peak day identification
            day_counts = filtered_df.groupby(filtered_df['Date'].dt.date).size()
            peak_day = day_counts.idxmax() if not day_counts.empty else None
            peak_count = day_counts.max() if not day_counts.empty else 0
            
            # Row 2 metrics
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Média de Resumos/Dia", f"{avg_per_day:.1f}")
            
            if peak_day:
                col2.metric("Dia com Mais Atividade", peak_day.strftime('%d/%m/%Y'), f"{peak_count} resumos")
            
            # Peak hour
            hour_counts = filtered_df['Hour'].value_counts()
            peak_hour = hour_counts.idxmax() if not hour_counts.empty else 0
            peak_hour_count = hour_counts.max() if not hour_counts.empty else 0
            col3.metric("Hora com Mais Atividade", f"{peak_hour}:00", f"{peak_hour_count} resumos")
            
            # Personal vs Group comparison
            personal_count = len(filtered_df[filtered_df['Send Type'].isin(['Personal', 'Group & Personal'])])
            group_count = len(filtered_df[filtered_df['Send Type'].isin(['Group', 'Group & Personal'])])
            personal_pct = personal_count / len(filtered_df) * 100
            col4.metric("Envios Pessoais", f"{personal_count}", f"{personal_pct:.1f}% do total")
        
        # Show activity timeline - summaries per day
        st.subheader("📅 Cronograma de Atividades")
        
        # Group by date and count
        timeline_data = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index(name='Count')
        timeline_data.columns = ['Date', 'Summaries']
        
        # Convert back to datetime for charting
        timeline_data['Date'] = pd.to_datetime(timeline_data['Date'])
        
        # Create a better timeline with Plotly
        fig = px.line(timeline_data, x='Date', y='Summaries', markers=True,
                     title='Resumos por Dia')
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Número de Resumos',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution by group and send type
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Resumos por Grupo")
            group_counts = filtered_df['Group Name'].value_counts().reset_index()
            group_counts.columns = ['Group', 'Count']
            
            fig = px.bar(group_counts, x='Group', y='Count', 
                        title='Total de Resumos por Grupo',
                        color='Count', text='Count')
            fig.update_layout(xaxis_title='Grupo', yaxis_title='Número de Resumos')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📤 Distribuição por Tipo de Envio")
            send_counts = filtered_df['Send Type'].value_counts().reset_index()
            send_counts.columns = ['Type', 'Count']
            
            fig = px.pie(send_counts, values='Count', names='Type', 
                        title='Distribuição por Tipo de Envio',
                        hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
        # Latest activity feed
        st.subheader("🕒 Atividades Recentes")
        
        # Show the 10 most recent log entries
        recent_df = filtered_df[['Timestamp', 'Group Name', 'Send Type']].head(10)
        recent_df['Timestamp'] = recent_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(recent_df, use_container_width=True)
    
    # Activity patterns
    st.header("⏰ Padrões de Atividade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Atividade por Dia da Semana")
        dow_counts = filtered_df['Day of Week'].value_counts().reset_index()
        dow_counts.columns = ['Day', 'Count']
        # Define correct order of days
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Map Portuguese day names if needed
        dow_map = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        # Create ordered series for chart
        ordered_dow = pd.DataFrame({
            'Day': dow_order,
            'Count': [dow_counts[dow_counts['Day'] == day]['Count'].sum() 
                      if day in dow_counts['Day'].values else 0 
                      for day in dow_order]
        })
        # Map day names if in Portuguese
        if 'Segunda' in dow_counts['Day'].values:
            ordered_dow['Day'] = ordered_dow['Day'].map(dow_map)
        
        st.bar_chart(ordered_dow.set_index('Day'))
    
    with col2:
        st.subheader("Atividade por Hora do Dia")
        hour_counts = filtered_df['Hour'].value_counts().reset_index()
        hour_counts.columns = ['Hour', 'Count']
        # Sort by hour
        hour_counts = hour_counts.sort_values('Hour')
        st.bar_chart(hour_counts.set_index('Hour'))
    
    # Activity heatmap by day and hour
    st.subheader("Heatmap de Atividade: Dia da Semana x Hora")
    
    # Create temp df for heatmap
    heatmap_df = filtered_df.copy()
    
    # Extract day of week and hour
    heatmap_df['Day of Week Num'] = heatmap_df['Timestamp'].dt.dayofweek
    heatmap_df['Hour'] = heatmap_df['Timestamp'].dt.hour
    
    # Create a pivot table for the heatmap
    day_hour_pivot = pd.pivot_table(
        heatmap_df, 
        values='Group ID',
        index='Day of Week Num', 
        columns='Hour', 
        aggfunc='count',
        fill_value=0
    )
    
    # Map day numbers to names
    day_names = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    day_hour_pivot.index = [day_names[i] for i in day_hour_pivot.index]
    
    # Display as a dataframe styled as a heatmap
    st.dataframe(
        day_hour_pivot,
        height=250,
        use_container_width=True
    )
    
    # Detailed group statistics
    st.header("👥 Estatísticas Detalhadas por Grupo")
    
    # Create a dataframe with group statistics
    group_stats = filtered_df.groupby('Group Name').agg({
        'Timestamp': ['count', 'max', 'min'],
        'Send Type': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
    })
    
    # Flatten multi-level columns
    group_stats.columns = ['Total Summaries', 'Last Activity', 'First Activity', 'Most Common Send Type']
    group_stats = group_stats.reset_index()
    
    # Add a column for activity days
    group_stats['Activity Days'] = group_stats.apply(
        lambda row: (row['Last Activity'] - row['First Activity']).days + 1, axis=1
    )
    
    # Add a column for average summaries per day
    group_stats['Avg Summaries/Day'] = group_stats['Total Summaries'] / group_stats['Activity Days']
    group_stats['Avg Summaries/Day'] = group_stats['Avg Summaries/Day'].round(2)
    
    # Show the table
    st.dataframe(group_stats.sort_values('Total Summaries', ascending=False), use_container_width=True)
    
    # Latest activity feed
    st.header("🕒 Atividades Recentes")
    
    # Show the 10 most recent log entries
    recent_df = filtered_df[['Timestamp', 'Group Name', 'Send Type']].head(10)
    recent_df['Timestamp'] = recent_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    st.dataframe(recent_df, use_container_width=True)
    
    # Monthly activity heatmap 
    st.header("📆 Heatmap de Atividade Mensal")
    
    # Create a DataFrame for heatmap (group by month and day)
    heatmap_df = filtered_df.copy()
    heatmap_df['Month'] = heatmap_df['Timestamp'].dt.month
    heatmap_df['Day'] = heatmap_df['Timestamp'].dt.day
    
    # Count occurrences for each month/day combination
    heatmap_data = heatmap_df.groupby(['Month', 'Day']).size().reset_index(name='Count')
    
    # Pivot the data for the heatmap
    pivot_table = heatmap_data.pivot(index='Day', columns='Month', values='Count').fillna(0)
    
    # Get month names for columns
    month_names = {i: calendar.month_name[i] for i in range(1, 13)}
    pivot_table.columns = [month_names.get(col, col) for col in pivot_table.columns]
    
    # Display the heatmap
    st.dataframe(pivot_table, use_container_width=True)
    
    # Group Activity and Efficiency Analysis
    st.header("🔍 Análise de Eficiência e Engajamento")
    
    # Calculate overall statistics
    total_days = (filtered_df['Timestamp'].max() - filtered_df['Timestamp'].min()).days + 1
    avg_summaries_per_day = len(filtered_df) / total_days if total_days > 0 else 0
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Período Total de Atividade", f"{total_days} dias")
    col2.metric("Média de Resumos/Dia", f"{avg_summaries_per_day:.2f}")
    
    # Group with highest engagement (most consistent activity)
    if not filtered_df.empty and len(filtered_df['Group Name'].unique()) > 1:
        # Get days with activity per group
        group_days = filtered_df.groupby('Group Name')['Date'].nunique()
        most_consistent_group = group_days.idxmax()
        most_consistent_days = group_days.max()
        
        # Get group with most varied send types (uses both personal and group)
        send_type_variety = filtered_df.groupby('Group Name')['Send Type'].nunique()
        most_varied_group = send_type_variety.idxmax()
        most_varied_count = send_type_variety.max()
        
        col3.metric("Grupo Mais Consistente", most_consistent_group, f"{most_consistent_days} dias de atividade")
        col4.metric("Grupo Mais Diversificado", most_varied_group, f"{most_varied_count} tipos de envio")
    
    # Growth trend analysis
    st.subheader("📈 Tendência de Crescimento")
    
    # Group data by month for trend analysis
    trend_df = filtered_df.copy()
    trend_df['Year-Month'] = trend_df['Timestamp'].dt.strftime('%Y-%m')
    monthly_counts = trend_df.groupby('Year-Month').size().reset_index(name='Count')
    
    # Calculate growth metrics
    if len(monthly_counts) > 1:
        first_month_count = monthly_counts.iloc[0]['Count']
        last_month_count = monthly_counts.iloc[-1]['Count']
        growth_rate = ((last_month_count / first_month_count) - 1) * 100 if first_month_count > 0 else 0
        
        growth_text = f"Crescimento de {growth_rate:.1f}% desde o início" if growth_rate >= 0 else f"Queda de {abs(growth_rate):.1f}% desde o início"
        
        # Show the growth trend
        st.write(f"**{growth_text}**")
        
        # Show monthly trend chart
        st.line_chart(monthly_counts.set_index('Year-Month'))
    else:
        st.write("Dados insuficientes para análise de tendência. São necessários pelo menos dois meses.")
    
    # Download option
    st.header("📥 Exportar Dados")
    
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        "Download CSV",
        csv,
        "whatsapp_summary_log.csv",
        "text/csv",
        key='download-csv'
    )
    
else:
    st.info("Não há dados de log disponíveis para exibição. / No log data available to display.")
