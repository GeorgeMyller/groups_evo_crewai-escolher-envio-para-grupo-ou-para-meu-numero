"""
Serviço de inicialização da infraestrutura de escalabilidade.
"""
import asyncio
import logging
from typing import Optional
import streamlit as st
from contextlib import asynccontextmanager

from config import config
from src.infrastructure.manager import InfrastructureManager

# Configurar logging estruturado
import structlog

logger = structlog.get_logger(__name__)

class InfrastructureService:
    """Serviço central para gerenciamento da infraestrutura."""
    
    def __init__(self):
        self.manager: Optional[InfrastructureManager] = None
        self._initialized = False
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager para o ciclo de vida da infraestrutura."""
        try:
            await self.start()
            yield self
        finally:
            await self.stop()
    
    async def start(self):
        """Inicializar todos os componentes da infraestrutura."""
        if self._initialized:
            return
        
        logger.info("🚀 Iniciando infraestrutura de escalabilidade...")
        
        try:
            # Inicializar o gerenciador de infraestrutura
            self.manager = InfrastructureManager()
            await self.manager.initialize()
            
            self._initialized = True
            logger.info("✅ Infraestrutura inicializada com sucesso")
            
            # Armazenar no session state do Streamlit
            if 'infrastructure' not in st.session_state:
                st.session_state.infrastructure = self
            
        except Exception as e:
            logger.error("❌ Erro ao inicializar infraestrutura", error=str(e))
            raise
    
    async def stop(self):
        """Parar todos os componentes da infraestrutura."""
        if not self._initialized or not self.manager:
            return
        
        logger.info("🛑 Parando infraestrutura...")
        
        try:
            self.manager.shutdown()
            self._initialized = False
            logger.info("✅ Infraestrutura parada com sucesso")
        except Exception as e:
            logger.error("❌ Erro ao parar infraestrutura", error=str(e))
    
    def get_cache(self):
        """Obter instância do cache Redis."""
        if self.manager and self.manager.cache_manager:
            return self.manager.cache_manager
        return None
    
    def get_metrics(self):
        """Obter instância do coletor de métricas."""
        if self.manager and self.manager.metrics_collector:
            return self.manager.metrics_collector
        return None
    
    def get_backup_manager(self):
        """Obter instância do gerenciador de backup."""
        if self.manager and self.manager.backup_manager:
            return self.manager.backup_manager
        return None
    
    async def health_check(self):
        """Verificar saúde de todos os componentes."""
        if not self.manager:
            return {"status": "not_initialized"}
        
        return await self.manager.get_health_status()
    
    async def get_metrics_data(self):
        """Obter dados de métricas para dashboard."""
        if not self.manager or not self.manager.metrics_collector:
            return {}
        
        try:
            # Coletar métricas do sistema
            system_metrics = self.manager.metrics_collector.get_metrics_summary()
            
            # Obter estatísticas do cache
            cache_stats = {}
            if self.manager.cache_manager:
                cache_stats = await self.manager.cache_manager.get_stats()
            
            return {
                "system": system_metrics,
                "cache": cache_stats,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error("Erro ao coletar métricas", error=str(e))
            return {}

# Instância global do serviço
infrastructure_service = InfrastructureService()

def get_infrastructure() -> InfrastructureService:
    """Obter instância do serviço de infraestrutura."""
    return infrastructure_service

async def init_infrastructure():
    """Inicializar infraestrutura de forma assíncrona."""
    try:
        await infrastructure_service.start()
        return True
    except Exception as e:
        logger.error("Falha na inicialização da infraestrutura", error=str(e))
        return False

def init_infrastructure_sync():
    """Inicializar infraestrutura de forma síncrona (para Streamlit)."""
    try:
        # Verificar se já foi inicializada no session state
        if 'infrastructure_initialized' in st.session_state:
            return st.session_state.infrastructure_initialized
        
        # Criar loop de eventos se não existir
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Inicializar infraestrutura
        result = loop.run_until_complete(init_infrastructure())
        st.session_state.infrastructure_initialized = result
        
        if result:
            st.session_state.infrastructure = infrastructure_service
            logger.info("✅ Infraestrutura inicializada no Streamlit")
        else:
            logger.error("❌ Falha na inicialização da infraestrutura")
        
        return result
        
    except Exception as e:
        logger.error("Erro na inicialização síncrona", error=str(e))
        st.session_state.infrastructure_initialized = False
        return False
