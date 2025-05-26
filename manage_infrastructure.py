#!/usr/bin/env python3
"""
Script de gerenciamento da infraestrutura WhatsApp Group Resumer.
"""
import asyncio
import click
import sys
import time
from pathlib import Path

# Adicionar diretório raiz ao PATH
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure_service import InfrastructureService
from config import config

@click.group()
def cli():
    """Gerenciador da infraestrutura WhatsApp Group Resumer."""
    pass

@cli.command()
def start():
    """Iniciar todos os serviços da infraestrutura."""
    click.echo("🚀 Iniciando infraestrutura...")
    
    async def _start():
        service = InfrastructureService()
        try:
            await service.start()
            click.echo("✅ Infraestrutura iniciada com sucesso!")
            
            # Manter rodando até interrupção
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n🛑 Parando infraestrutura...")
                await service.stop()
                click.echo("✅ Infraestrutura parada com sucesso!")
        except Exception as e:
            click.echo(f"❌ Erro: {e}")
            sys.exit(1)
    
    asyncio.run(_start())

@cli.command()
def health():
    """Verificar saúde da infraestrutura."""
    click.echo("🔍 Verificando saúde da infraestrutura...")
    
    async def _health():
        service = InfrastructureService()
        try:
            await service.start()
            health_status = await service.health_check()
            
            click.echo(f"\n📊 Status geral: {health_status.get('overall_status', 'unknown')}")
            
            components = health_status.get('components', {})
            
            # Cache
            cache_status = components.get('cache', {})
            if cache_status.get('healthy'):
                click.echo("✅ Cache Redis: Conectado")
            else:
                click.echo(f"❌ Cache Redis: {cache_status.get('error', 'Erro desconhecido')}")
            
            # Métricas
            monitoring_status = components.get('monitoring', {})
            if monitoring_status.get('status') == 'healthy':
                click.echo("✅ Sistema de Métricas: Ativo")
            else:
                click.echo(f"❌ Sistema de Métricas: {monitoring_status.get('status', 'Erro desconhecido')}")
            
            # Backup
            backup_status = components.get('backup', {})
            if backup_status.get('status') == 'healthy':
                click.echo("✅ Sistema de Backup: Configurado")
            else:
                click.echo(f"❌ Sistema de Backup: {backup_status.get('status', 'Erro desconhecido')}")
            
            await service.stop()
            
        except Exception as e:
            click.echo(f"❌ Erro ao verificar saúde: {e}")
            sys.exit(1)
    
    asyncio.run(_health())

@cli.command()
def metrics():
    """Exibir métricas do sistema."""
    click.echo("📈 Coletando métricas...")
    
    async def _metrics():
        service = InfrastructureService()
        try:
            await service.start()
            metrics_data = await service.get_metrics_data()
            
            if 'system' in metrics_data:
                system = metrics_data['system']
                click.echo(f"\n💻 Sistema:")
                click.echo(f"  CPU: {system.get('cpu_percent', 0):.1f}%")
                click.echo(f"  Memória: {system.get('memory_percent', 0):.1f}%")
                click.echo(f"  Disco: {system.get('disk_percent', 0):.1f}%")
            
            if 'cache' in metrics_data:
                cache = metrics_data['cache']
                click.echo(f"\n💾 Cache:")
                click.echo(f"  Chaves: {cache.get('total_keys', 0)}")
                click.echo(f"  Taxa de acerto: {cache.get('hit_rate', 0):.1f}%")
                click.echo(f"  Uso de memória: {cache.get('memory_usage', 0):.2f} MB")
            
            await service.stop()
            
        except Exception as e:
            click.echo(f"❌ Erro ao coletar métricas: {e}")
            sys.exit(1)
    
    asyncio.run(_metrics())

@cli.group()
def cache():
    """Gerenciar cache Redis."""
    pass

@cache.command()
def clear():
    """Limpar todo o cache."""
    click.echo("🗑️ Limpando cache...")
    
    async def _clear():
        service = InfrastructureService()
        try:
            await service.start()
            cache = service.get_cache()
            
            if cache:
                await cache.clear_all()
                click.echo("✅ Cache limpo com sucesso!")
            else:
                click.echo("❌ Cache não disponível")
            
            await service.stop()
            
        except Exception as e:
            click.echo(f"❌ Erro ao limpar cache: {e}")
            sys.exit(1)
    
    asyncio.run(_clear())

@cache.command()
def stats():
    """Exibir estatísticas do cache."""
    click.echo("📊 Estatísticas do cache...")
    
    async def _stats():
        service = InfrastructureService()
        try:
            await service.start()
            cache = service.get_cache()
            
            if cache:
                stats = await cache.get_stats()
                click.echo(f"\n💾 Estatísticas do Cache:")
                click.echo(f"  Total de chaves: {stats.get('total_keys', 0)}")
                click.echo(f"  Taxa de acerto: {stats.get('hit_rate', 0):.1f}%")
                click.echo(f"  Taxa de erro: {stats.get('miss_rate', 0):.1f}%")
                click.echo(f"  Uso de memória: {stats.get('memory_usage', 0):.2f} MB")
                click.echo(f"  Uptime: {stats.get('uptime', 0)} segundos")
            else:
                click.echo("❌ Cache não disponível")
            
            await service.stop()
            
        except Exception as e:
            click.echo(f"❌ Erro ao obter estatísticas: {e}")
            sys.exit(1)
    
    asyncio.run(_stats())

@cli.command()
def backup():
    """Realizar backup manual."""
    click.echo("💾 Realizando backup...")
    
    async def _backup():
        service = InfrastructureService()
        try:
            await service.start()
            backup_manager = service.get_backup_manager()
            
            if backup_manager:
                backup_path = await backup_manager.create_full_backup()
                click.echo(f"✅ Backup realizado: {backup_path}")
            else:
                click.echo("❌ Sistema de backup não disponível")
            
            await service.stop()
            
        except Exception as e:
            click.echo(f"❌ Erro no backup: {e}")
            sys.exit(1)
    
    asyncio.run(_backup())

@cli.command()
def config_check():
    """Verificar configuração do sistema."""
    click.echo("⚙️ Verificando configuração...")
    
    click.echo(f"\n🔧 Configurações:")
    click.echo(f"  Debug: {config.debug}")
    click.echo(f"  Log Level: {config.log_level}")
    
    click.echo(f"\n🔄 Redis:")
    click.echo(f"  Host: {config.redis.host}")
    click.echo(f"  Porta: {config.redis.port}")
    click.echo(f"  Database: {config.redis.db}")
    click.echo(f"  Habilitado: {config.redis.enabled}")
    
    click.echo(f"\n📊 Métricas:")
    click.echo(f"  Habilitado: {config.metrics.enabled}")
    click.echo(f"  Porta: {config.metrics.port}")
    click.echo(f"  Intervalo: {config.metrics.collection_interval}s")
    
    click.echo(f"\n💾 Backup:")
    click.echo(f"  Habilitado: {config.backup.enabled}")
    click.echo(f"  Retenção: {config.backup.retention_days} dias")
    click.echo(f"  Compressão: {config.backup.compression}")
    click.echo(f"  Agendamento: {config.backup.schedule}")

if __name__ == '__main__':
    cli()
