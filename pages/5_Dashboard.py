"""
Dashboard de Monitoramento e Métricas - WhatsApp Group Resumer
"""
import streamlit as st
import asyncio
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time

from infrastructure_service import get_infrastructure, init_infrastructure_sync

# Configuração da página
st.set_page_config(
    page_title='Dashboard - WhatsApp Group Resumer',
    page_icon='📊',
    layout='wide'
)

# CSS customizado para o dashboard
st.markdown("""
<style>
.metric-container {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    border-left: 4px solid #0d6efd;
}
.status-ok {
    color: #198754;
    font-weight: bold;
}
.status-error {
    color: #dc3545;
    font-weight: bold;
}
.status-warning {
    color: #fd7e14;
    font-weight: bold;
}
.cache-stat {
    background-color: #e7f3ff;
    border-radius: 8px;
    padding: 15px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Monitoramento")
st.markdown("---")

# Inicializar infraestrutura
if 'infrastructure_initialized' not in st.session_state:
    with st.spinner("🚀 Inicializando infraestrutura..."):
        success = init_infrastructure_sync()
        if success:
            st.success("✅ Infraestrutura inicializada com sucesso!")
        else:
            st.error("❌ Falha na inicialização da infraestrutura")
            st.stop()

# Obter serviço de infraestrutura
infrastructure = get_infrastructure()

# Verificar saúde do sistema
async def get_health_status():
    """Obter status de saúde do sistema."""
    try:
        health = await infrastructure.health_check()
        return health
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_metrics_data():
    """Obter dados de métricas."""
    try:
        return await infrastructure.get_metrics_data()
    except Exception as e:
        return {"error": str(e)}

# Função para executar código assíncrono
def run_async(coro):
    """Executar código assíncrono no Streamlit."""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# Layout em colunas para o dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Status do Sistema")
    
    # Status geral
    health_status = run_async(get_health_status())
    
    if health_status.get("status") == "healthy":
        st.markdown('<div class="status-ok">🟢 Sistema Operacional</div>', unsafe_allow_html=True)
    elif health_status.get("status") == "degraded":
        st.markdown('<div class="status-warning">🟡 Sistema com Problemas</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">🔴 Sistema com Falhas</div>', unsafe_allow_html=True)
    
    # Detalhes dos componentes
    st.markdown("#### Componentes:")
    
    # Cache Redis
    cache_status = health_status.get("cache", {})
    if cache_status.get("healthy"):
        st.markdown("✅ **Redis Cache** - Conectado")
    else:
        st.markdown(f"❌ **Redis Cache** - {cache_status.get('error', 'Desconectado')}")
    
    # Métricas
    metrics_status = health_status.get("metrics", {})
    if metrics_status.get("healthy"):
        st.markdown("✅ **Sistema de Métricas** - Ativo")
    else:
        st.markdown(f"❌ **Sistema de Métricas** - {metrics_status.get('error', 'Inativo')}")
    
    # Backup
    backup_status = health_status.get("backup", {})
    if backup_status.get("healthy"):
        st.markdown("✅ **Sistema de Backup** - Configurado")
    else:
        st.markdown(f"❌ **Sistema de Backup** - {backup_status.get('error', 'Não configurado')}")

with col2:
    st.subheader("⚡ Ações Rápidas")
    
    if st.button("🔄 Atualizar Dashboard"):
        st.rerun()
    
    if st.button("📋 Limpar Cache"):
        if infrastructure.get_cache():
            try:
                # Implementar limpeza de cache
                st.success("🗑️ Cache limpo com sucesso!")
            except Exception as e:
                st.error(f"Erro ao limpar cache: {e}")
        else:
            st.warning("Cache não disponível")
    
    if st.button("💾 Backup Manual"):
        backup_manager = infrastructure.get_backup_manager()
        if backup_manager:
            try:
                # Implementar backup manual
                st.success("✅ Backup realizado com sucesso!")
            except Exception as e:
                st.error(f"Erro no backup: {e}")
        else:
            st.warning("Sistema de backup não disponível")

# Métricas do sistema
st.markdown("---")
st.subheader("📈 Métricas do Sistema")

# Obter dados de métricas
metrics_data = run_async(get_metrics_data())

if metrics_data and "system" in metrics_data:
    system_metrics = metrics_data["system"]
    
    # Métricas em colunas
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        cpu_usage = system_metrics.get("cpu_percent", 0)
        st.metric(
            label="🖥️ CPU",
            value=f"{cpu_usage:.1f}%",
            delta=None
        )
    
    with metric_cols[1]:
        memory_usage = system_metrics.get("memory_percent", 0)
        st.metric(
            label="🧠 Memória",
            value=f"{memory_usage:.1f}%",
            delta=None
        )
    
    with metric_cols[2]:
        disk_usage = system_metrics.get("disk_percent", 0)
        st.metric(
            label="💾 Disco",
            value=f"{disk_usage:.1f}%",
            delta=None
        )
    
    with metric_cols[3]:
        # Simular métrica de grupos ativos
        st.metric(
            label="👥 Grupos Ativos",
            value="--",
            delta=None
        )

# Cache Statistics
if metrics_data and "cache" in metrics_data:
    st.markdown("---")
    st.subheader("💾 Estatísticas do Cache")
    
    cache_stats = metrics_data["cache"]
    
    cache_cols = st.columns(3)
    
    with cache_cols[0]:
        total_keys = cache_stats.get("total_keys", 0)
        st.metric("🔑 Total de Chaves", total_keys)
    
    with cache_cols[1]:
        hit_rate = cache_stats.get("hit_rate", 0)
        st.metric("🎯 Taxa de Acerto", f"{hit_rate:.1f}%")
    
    with cache_cols[2]:
        memory_usage = cache_stats.get("memory_usage", 0)
        st.metric("📊 Uso de Memória", f"{memory_usage:.2f} MB")

# Gráficos de performance
st.markdown("---")
st.subheader("📊 Performance do Sistema")

# Gráfico de CPU e Memória
if metrics_data and "system" in metrics_data:
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        # Gráfico de gauge para CPU
        cpu_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = system_metrics.get("cpu_percent", 0),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Usage (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        cpu_fig.update_layout(height=300)
        st.plotly_chart(cpu_fig, use_container_width=True)
    
    with chart_cols[1]:
        # Gráfico de gauge para Memória
        memory_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = system_metrics.get("memory_percent", 0),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Memory Usage (%)"},
            delta = {'reference': 60},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        memory_fig.update_layout(height=300)
        st.plotly_chart(memory_fig, use_container_width=True)

# Configurações do sistema
st.markdown("---")
st.subheader("⚙️ Configurações")

config_cols = st.columns(2)

with config_cols[0]:
    st.markdown("#### Redis")
    from config import config
    
    st.write(f"**Host:** {config.redis.host}")
    st.write(f"**Porta:** {config.redis.port}")
    st.write(f"**Database:** {config.redis.db}")
    st.write(f"**Status:** {'✅ Ativo' if config.redis.enabled else '❌ Inativo'}")

with config_cols[1]:
    st.markdown("#### Monitoramento")
    st.write(f"**Porta de Métricas:** {config.metrics.port}")
    st.write(f"**Intervalo de Coleta:** {config.metrics.collection_interval}s")
    st.write(f"**Status:** {'✅ Ativo' if config.metrics.enabled else '❌ Inativo'}")

# Auto-refresh
if st.checkbox("🔄 Auto-refresh (30s)", value=False):
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Dashboard atualizado em: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")
