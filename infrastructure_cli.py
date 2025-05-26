#!/usr/bin/env python3
"""
CLI para gerenciamento de infraestrutura sem dependências Streamlit

Este arquivo fornece funcionalidades CLI sem importar Streamlit,
evitando warnings quando usado fora do contexto Streamlit.
"""

import asyncio
import click
import structlog
from datetime import datetime
from typing import Dict, Any

# Importar apenas componentes necessários sem Streamlit
from src.infrastructure.manager import InfrastructureManager
from src.infrastructure.cache.redis_cache import CacheConfig
from src.infrastructure.monitoring.metrics import MonitoringConfig
from src.infrastructure.backup.backup_manager import BackupConfig

logger = structlog.get_logger(__name__)

@click.group()
def cli():
    """Gerenciamento de infraestrutura de escalabilidade."""
    pass

@cli.command()
def health():
    """Verificar saúde da infraestrutura."""
    click.echo("🔍 Verificando saúde da infraestrutura...")
    
    # Criar manager sem Streamlit
    manager = InfrastructureManager()
    
    # Configurar componentes
    cache_config = CacheConfig()
    monitoring_config = MonitoringConfig()
    backup_config = BackupConfig()
    
    async def run_health_check():
        try:
            # Inicializar infraestrutura
            init_result = await manager.initialize(
                cache_config=cache_config,
                monitoring_config=monitoring_config,
                backup_config=backup_config
            )
            
            # Usar resultado da inicialização em vez de health check separado
            # pois contém informações mais completas
            show_health_results(init_result)
            
            # Shutdown
            manager.shutdown()
            
        except Exception as e:
            click.echo(f"❌ Erro ao verificar saúde: {e}")
            logger.error("Health check failed", error=str(e))
    
    # Executar
    asyncio.run(run_health_check())

def show_health_results(health_status: Dict[str, Any]):
    """Mostrar resultados de saúde."""
    components = health_status.get('components', {})
    overall_status = health_status.get('overall_status', 'unknown')
    
    click.echo(f"\n📊 Status geral: {overall_status}")
    
    # Debug: print actual structure
    # click.echo(f"DEBUG - Components: {components}")
    
    # Cache Redis
    cache_info = components.get('cache', {})
    cache_status = cache_info.get('status', 'unknown')
    cache_connected = cache_info.get('connected', False)
    if cache_status == 'healthy' and cache_connected:
        click.echo("✅ Cache Redis: Conectado")
    else:
        click.echo("❌ Cache Redis: Não conectado")
    
    # Métricas
    metrics_info = components.get('monitoring', {})
    server_running = metrics_info.get('server_running', False)
    if server_running:
        port = metrics_info.get('port', 'unknown')
        click.echo(f"✅ Sistema de Métricas: Ativo (porta {port})")
    else:
        click.echo("❌ Sistema de Métricas: Inativo")
    
    # Backup
    backup_info = components.get('backup', {})
    backup_status = backup_info.get('status', 'unknown')
    backup_enabled = backup_info.get('enabled', False)
    if backup_status == 'initialized' and backup_enabled:
        backup_dir = backup_info.get('backup_directory', 'unknown')
        click.echo(f"✅ Sistema de Backup: Configurado ({backup_dir})")
    else:
        click.echo("❌ Sistema de Backup: Não configurado")

@cli.group()
def cache():
    """Gerenciamento de cache."""
    pass

@cache.command()
def stats():
    """Estatísticas do cache."""
    click.echo("📊 Estatísticas do cache...")
    
    manager = InfrastructureManager()
    
    async def run_cache_stats():
        try:
            # Configurar
            cache_config = CacheConfig()
            monitoring_config = MonitoringConfig()
            backup_config = BackupConfig()
            
            # Inicializar
            await manager.initialize(
                cache_config=cache_config,
                monitoring_config=monitoring_config,
                backup_config=backup_config
            )
            
            # Obter estatísticas
            cache_stats = await manager.cache_manager.get_stats()
            
            # Mostrar resultado
            show_cache_stats(cache_stats)
            
            # Shutdown
            manager.shutdown()
            
        except Exception as e:
            click.echo(f"❌ Erro ao obter estatísticas: {e}")
            logger.error("Cache stats failed", error=str(e))
    
    asyncio.run(run_cache_stats())

def show_cache_stats(stats: Dict[str, Any]):
    """Mostrar estatísticas do cache."""
    click.echo("\n💾 Estatísticas do Cache:")
    click.echo(f"  Total de chaves: {stats.get('total_keys', 0)}")
    
    hits = stats.get('hits', 0)
    misses = stats.get('misses', 0)
    total = hits + misses
    
    if total > 0:
        hit_rate = (hits / total) * 100
    else:
        hit_rate = 100.0
    
    click.echo(f"  Taxa de acerto: {hit_rate:.1f}%")
    click.echo(f"  Taxa de erro: {100 - hit_rate:.1f}%")
    click.echo(f"  Uso de memória: {stats.get('memory_usage_mb', 0):.2f} MB")
    click.echo(f"  Uptime: {stats.get('uptime_seconds', 0)} segundos")

@cli.command()
def metrics():
    """Coletar métricas do sistema."""
    click.echo("📈 Coletando métricas...")
    
    manager = InfrastructureManager()
    
    async def run_metrics():
        try:
            # Configurar
            cache_config = CacheConfig()
            monitoring_config = MonitoringConfig()
            backup_config = BackupConfig()
            
            # Inicializar
            await manager.initialize(
                cache_config=cache_config,
                monitoring_config=monitoring_config,
                backup_config=backup_config
            )
            
            # Obter métricas
            metrics_summary = manager.metrics_collector.get_metrics_summary()
            
            # Mostrar resultado
            show_metrics(metrics_summary)
            
            # Shutdown
            manager.shutdown()
            
        except Exception as e:
            click.echo(f"❌ Erro ao coletar métricas: {e}")
            logger.error("Metrics collection failed", error=str(e))
    
    asyncio.run(run_metrics())

def show_metrics(metrics: Dict[str, Any]):
    """Mostrar métricas."""
    click.echo("\n💻 Sistema:")
    system_metrics = metrics.get('system', {})
    click.echo(f"  CPU: {system_metrics.get('cpu_percent', 0)}%")
    
    memory = system_metrics.get('memory', {})
    memory_percent = memory.get('percent', 0)
    click.echo(f"  Memória: {memory_percent}%")
    
    disk = system_metrics.get('disk', {})
    disk_percent = disk.get('percent', 0)
    click.echo(f"  Disco: {disk_percent}%")
    
    click.echo("\n💾 Cache:")
    cache_metrics = metrics.get('cache', {})
    click.echo(f"  Chaves: {cache_metrics.get('total_keys', 0)}")
    
    hits = cache_metrics.get('hits', 0)
    misses = cache_metrics.get('misses', 0)
    total = hits + misses
    
    if total > 0:
        hit_rate = (hits / total) * 100
    else:
        hit_rate = 100.0
    
    click.echo(f"  Taxa de acerto: {hit_rate:.1f}%")
    click.echo(f"  Uso de memória: {cache_metrics.get('memory_usage_mb', 0):.2f} MB")

@cli.command()
@click.option('--groups-file', help='Arquivo CSV com dados dos grupos para aquecer o cache')
def warm_cache(groups_file):
    """Aquecer cache com dados para melhor performance."""
    click.echo("🔥 Aquecendo cache...")
    
    # Criar manager
    manager = InfrastructureManager()
    
    async def run_cache_warming():
        try:
            # Inicializar infraestrutura
            cache_config = CacheConfig()
            await manager.initialize(cache_config=cache_config)
            
            # Carregar dados dos grupos se fornecido
            groups_data = None
            if groups_file:
                import pandas as pd
                try:
                    df = pd.read_csv(groups_file)
                    groups_data = df.to_dict('records')
                    click.echo(f"📊 Carregados {len(groups_data)} grupos do arquivo")
                except Exception as e:
                    click.echo(f"⚠️ Erro ao carregar arquivo: {e}")
                    groups_data = None
            
            # Aquecer cache
            warming_result = await manager.warm_cache_with_groups(groups_data)
            
            if warming_result["status"] == "success":
                click.echo(f"✅ Cache aquecido com sucesso!")
                click.echo(f"   🔑 Chaves aquecidas: {warming_result['warmed_keys']}")
                if warming_result.get("errors"):
                    click.echo(f"   ⚠️ Erros: {len(warming_result['errors'])}")
                    for error in warming_result["errors"][:3]:  # Mostrar só os primeiros 3
                        click.echo(f"      • {error}")
            else:
                click.echo(f"❌ Falha no aquecimento: {warming_result.get('message')}")
            
        except Exception as e:
            click.echo(f"❌ Erro no aquecimento: {e}")
        finally:
            manager.shutdown()
    
    # Executar
    asyncio.run(run_cache_warming())

@cli.command()
def cache_info():
    """Obter informações detalhadas do cache."""
    click.echo("📊 Coletando informações do cache...")
    
    manager = InfrastructureManager()
    
    async def run_cache_info():
        try:
            # Inicializar
            cache_config = CacheConfig()
            await manager.initialize(cache_config=cache_config)
            
            # Obter informações
            cache_info = await manager.get_cache_info()
            
            if cache_info["status"] == "connected":
                click.echo("💾 Informações do Cache Redis:")
                click.echo(f"  🔑 Total de chaves: {cache_info['total_keys']}")
                click.echo(f"  💿 Memória usada: {cache_info['memory']['used_memory_human']}")
                click.echo(f"  📈 Pico de memória: {cache_info['memory']['used_memory_peak_human']}")
                click.echo(f"  🔗 Versão Redis: {cache_info['redis_version']}")
                click.echo(f"  👥 Clientes conectados: {cache_info['connected_clients']}")
                click.echo(f"  ⏱️ Uptime: {cache_info['uptime_in_seconds']}s")
                
                # Estatísticas de performance
                stats = cache_info['stats']
                click.echo(f"  📊 Operações: {stats['operations']}")
                click.echo(f"  ✅ Hits: {stats['hits']}")
                click.echo(f"  ❌ Misses: {stats['misses']}")
                
                total_ops = stats['hits'] + stats['misses']
                if total_ops > 0:
                    hit_rate = (stats['hits'] / total_ops) * 100
                    click.echo(f"  🎯 Taxa de acerto: {hit_rate:.1f}%")
                
            else:
                click.echo(f"❌ Cache: {cache_info['status']}")
                if 'error' in cache_info:
                    click.echo(f"   Erro: {cache_info['error']}")
            
        except Exception as e:
            click.echo(f"❌ Erro ao obter informações: {e}")
        finally:
            manager.shutdown()
    
    # Executar
    asyncio.run(run_cache_info())

@cli.command()
@click.option('--keys', '-k', multiple=True, help='Chaves específicas para obter do cache')
def cache_get(keys):
    """Obter valores do cache."""
    if not keys:
        click.echo("❌ Especifique pelo menos uma chave com --keys")
        return
    
    click.echo(f"🔍 Obtendo {len(keys)} chave(s) do cache...")
    
    manager = InfrastructureManager()
    
    async def run_cache_get():
        try:
            # Inicializar
            cache_config = CacheConfig()
            await manager.initialize(cache_config=cache_config)
            
            # Obter valores
            results = await manager.batch_cache_operation("get", list(keys))
            
            if results["status"] == "success":
                click.echo("📋 Resultados:")
                for key, value in results["results"].items():
                    if value is not None:
                        # Truncar valor longo para exibição
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        click.echo(f"  🔑 {key}: {value_str}")
                    else:
                        click.echo(f"  🔑 {key}: (não encontrado)")
            else:
                click.echo(f"❌ Erro: {results['message']}")
            
        except Exception as e:
            click.echo(f"❌ Erro ao obter valores: {e}")
        finally:
            manager.shutdown()
    
    # Executar
    asyncio.run(run_cache_get())

@cli.command()
@click.option('--pattern', '-p', help='Padrão para limpar (ex: group:*)')
@click.option('--all', 'clear_all', is_flag=True, help='Limpar todo o cache')
def cache_clear(pattern, clear_all):
    """Limpar dados do cache."""
    if not pattern and not clear_all:
        click.echo("❌ Especifique --pattern ou --all")
        return
    
    if clear_all:
        if not click.confirm("🚨 Tem certeza que quer limpar TODO o cache?"):
            click.echo("❌ Operação cancelada")
            return
    
    click.echo("🧹 Limpando cache...")
    
    manager = InfrastructureManager()
    
    async def run_cache_clear():
        try:
            # Inicializar
            cache_config = CacheConfig()
            await manager.initialize(cache_config=cache_config)
            
            if clear_all:
                # Limpar tudo
                success = await manager.cache_manager.clear_all()
                if success:
                    click.echo("✅ Cache completamente limpo")
                else:
                    click.echo("❌ Erro ao limpar cache")
            else:
                # Limpar por padrão
                deleted = await manager.cache_manager.delete_pattern(pattern)
                click.echo(f"✅ {deleted} chave(s) removida(s)")
            
        except Exception as e:
            click.echo(f"❌ Erro ao limpar cache: {e}")
        finally:
            manager.shutdown()
    
    # Executar
    asyncio.run(run_cache_clear())

# ...existing code...
