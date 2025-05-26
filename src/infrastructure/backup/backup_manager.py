"""
Backup System for Configurations and Data

PT-BR:
Sistema de backup automático para configurações, grupos,
resumos e dados críticos do sistema.

EN:
Automatic backup system for configurations, groups,
summaries and critical system data.
"""

import os
import json
import shutil
import zipfile
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import structlog
import os

logger = structlog.get_logger(__name__)


class BackupConfig:
    """
    PT-BR: Configurações do sistema de backup
    EN: Backup system configuration
    """
    def __init__(self):
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_dir = os.getenv("BACKUP_DIR", "./backups")
        self.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        self.backup_schedule_hours = [6, 18]  # 6h e 18h
        self.backup_compress = os.getenv("BACKUP_COMPRESS", "true").lower() == "true"
        self.backup_include_cache = os.getenv("BACKUP_INCLUDE_CACHE", "false").lower() == "true"
        self.backup_include_logs = os.getenv("BACKUP_INCLUDE_LOGS", "true").lower() == "true"
        
        # Configurações específicas
        self.max_backup_size_mb = int(os.getenv("BACKUP_MAX_SIZE_MB", "1000"))  # 1GB
        self.backup_format = os.getenv("BACKUP_FORMAT", "json")  # json, csv, both


class BackupManager:
    """
    PT-BR:
    Gerenciador de backup para dados e configurações do sistema.
    Suporta backup automático, compressão e limpeza de arquivos antigos.
    
    EN:
    Backup manager for system data and configurations.
    Supports automatic backup, compression and old file cleanup.
    """
    
    def __init__(self, config: Optional[BackupConfig] = None):
        self.config = config or BackupConfig()
        self.backup_path = Path(self.config.backup_dir)
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """
        PT-BR: Garante que diretório de backup existe
        EN: Ensure backup directory exists
        """
        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)
            logger.info("Backup directory ready", path=str(self.backup_path))
        except Exception as e:
            logger.error("Failed to create backup directory", path=str(self.backup_path), error=str(e))
            raise
    
    def _generate_backup_filename(self, data_type: str, extension: str = "json") -> str:
        """
        PT-BR: Gera nome de arquivo de backup
        EN: Generate backup filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{data_type}_backup_{timestamp}.{extension}"
    
    def _get_file_size_mb(self, file_path: Path) -> float:
        """
        PT-BR: Retorna tamanho do arquivo em MB
        EN: Return file size in MB
        """
        return file_path.stat().st_size / (1024 * 1024)
    
    def backup_groups_data(self, groups_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        PT-BR:
        Realiza backup dos dados de grupos.
        
        Parâmetros:
            groups_data: Lista de dados dos grupos
            
        Retorna:
            Dict: Resultado do backup
            
        EN:
        Backup groups data.
        
        Parameters:
            groups_data: List of groups data
            
        Returns:
            Dict: Backup result
        """
        if not self.config.backup_enabled:
            return {"status": "disabled", "message": "Backup is disabled"}
        
        try:
            timestamp = datetime.now()
            backup_info = {
                "timestamp": timestamp.isoformat(),
                "data_type": "groups",
                "total_groups": len(groups_data),
                "backup_version": "1.0"
            }
            
            # Preparar dados para backup
            backup_data = {
                "metadata": backup_info,
                "groups": groups_data
            }
            
            result = {"files_created": []}
            
            # Backup JSON
            if self.config.backup_format in ["json", "both"]:
                json_filename = self._generate_backup_filename("groups", "json")
                json_path = self.backup_path / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
                
                result["files_created"].append({
                    "filename": json_filename,
                    "path": str(json_path),
                    "size_mb": round(self._get_file_size_mb(json_path), 2),
                    "format": "json"
                })
            
            # Backup CSV
            if self.config.backup_format in ["csv", "both"]:
                csv_filename = self._generate_backup_filename("groups", "csv")
                csv_path = self.backup_path / csv_filename
                
                # Converter para DataFrame e salvar
                df = pd.DataFrame(groups_data)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                result["files_created"].append({
                    "filename": csv_filename,
                    "path": str(csv_path),
                    "size_mb": round(self._get_file_size_mb(csv_path), 2),
                    "format": "csv"
                })
            
            # Comprimir se habilitado
            if self.config.backup_compress:
                zip_filename = self._generate_backup_filename("groups", "zip")
                zip_path = self.backup_path / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_info in result["files_created"]:
                        zipf.write(file_info["path"], file_info["filename"])
                        # Remover arquivo original após compressão
                        os.remove(file_info["path"])
                
                result["files_created"] = [{
                    "filename": zip_filename,
                    "path": str(zip_path),
                    "size_mb": round(self._get_file_size_mb(zip_path), 2),
                    "format": "zip",
                    "compressed": True
                }]
            
            # Verificar tamanho máximo
            total_size = sum(file_info["size_mb"] for file_info in result["files_created"])
            if total_size > self.config.max_backup_size_mb:
                logger.warning(
                    "Backup size exceeds limit",
                    total_size_mb=total_size,
                    limit_mb=self.config.max_backup_size_mb
                )
            
            result.update({
                "status": "success",
                "timestamp": timestamp.isoformat(),
                "total_size_mb": round(total_size, 2),
                "groups_count": len(groups_data)
            })
            
            logger.info("Groups backup completed successfully", **result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Groups backup failed", **error_result)
            return error_result
    
    def backup_summaries_data(self, summaries_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        PT-BR:
        Realiza backup dos resumos gerados.
        
        Parâmetros:
            summaries_data: Lista de resumos
            
        Retorna:
            Dict: Resultado do backup
            
        EN:
        Backup generated summaries.
        
        Parameters:
            summaries_data: List of summaries
            
        Returns:
            Dict: Backup result
        """
        if not self.config.backup_enabled:
            return {"status": "disabled", "message": "Backup is disabled"}
        
        try:
            timestamp = datetime.now()
            backup_info = {
                "timestamp": timestamp.isoformat(),
                "data_type": "summaries",
                "total_summaries": len(summaries_data),
                "backup_version": "1.0"
            }
            
            backup_data = {
                "metadata": backup_info,
                "summaries": summaries_data
            }
            
            filename = self._generate_backup_filename("summaries", "json")
            file_path = self.backup_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            result = {
                "status": "success",
                "filename": filename,
                "path": str(file_path),
                "size_mb": round(self._get_file_size_mb(file_path), 2),
                "timestamp": timestamp.isoformat(),
                "summaries_count": len(summaries_data)
            }
            
            logger.info("Summaries backup completed successfully", **result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Summaries backup failed", **error_result)
            return error_result
    
    def backup_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PT-BR:
        Realiza backup das configurações do sistema.
        
        Parâmetros:
            config_data: Dados de configuração
            
        Retorna:
            Dict: Resultado do backup
            
        EN:
        Backup system configuration.
        
        Parameters:
            config_data: Configuration data
            
        Returns:
            Dict: Backup result
        """
        if not self.config.backup_enabled:
            return {"status": "disabled", "message": "Backup is disabled"}
        
        try:
            timestamp = datetime.now()
            backup_info = {
                "timestamp": timestamp.isoformat(),
                "data_type": "configuration",
                "backup_version": "1.0"
            }
            
            backup_data = {
                "metadata": backup_info,
                "configuration": config_data
            }
            
            filename = self._generate_backup_filename("config", "json")
            file_path = self.backup_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            result = {
                "status": "success",
                "filename": filename,
                "path": str(file_path),
                "size_mb": round(self._get_file_size_mb(file_path), 2),
                "timestamp": timestamp.isoformat(),
                "config_keys": len(config_data)
            }
            
            logger.info("Configuration backup completed successfully", **result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Configuration backup failed", **error_result)
            return error_result
    
    def create_full_backup(self, groups_data: List[Dict], summaries_data: List[Dict], 
                          config_data: Dict) -> Dict[str, Any]:
        """
        PT-BR:
        Cria backup completo do sistema.
        
        Parâmetros:
            groups_data: Dados dos grupos
            summaries_data: Dados dos resumos
            config_data: Dados de configuração
            
        Retorna:
            Dict: Resultado do backup completo
            
        EN:
        Create full system backup.
        
        Parameters:
            groups_data: Groups data
            summaries_data: Summaries data
            config_data: Configuration data
            
        Returns:
            Dict: Full backup result
        """
        if not self.config.backup_enabled:
            return {"status": "disabled", "message": "Backup is disabled"}
        
        try:
            timestamp = datetime.now()
            
            # Backup individual de cada tipo
            groups_result = self.backup_groups_data(groups_data)
            summaries_result = self.backup_summaries_data(summaries_data)
            config_result = self.backup_configuration(config_data)
            
            # Criar backup consolidado
            full_backup_data = {
                "metadata": {
                    "timestamp": timestamp.isoformat(),
                    "backup_type": "full_system",
                    "backup_version": "1.0",
                    "components": ["groups", "summaries", "configuration"]
                },
                "groups": groups_data,
                "summaries": summaries_data,
                "configuration": config_data
            }
            
            filename = self._generate_backup_filename("full_system", "json")
            file_path = self.backup_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(full_backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            # Comprimir backup completo
            if self.config.backup_compress:
                zip_filename = self._generate_backup_filename("full_system", "zip")
                zip_path = self.backup_path / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, filename)
                
                os.remove(file_path)
                final_path = zip_path
                final_filename = zip_filename
            else:
                final_path = file_path
                final_filename = filename
            
            result = {
                "status": "success",
                "timestamp": timestamp.isoformat(),
                "backup_type": "full_system",
                "filename": final_filename,
                "path": str(final_path),
                "size_mb": round(self._get_file_size_mb(final_path), 2),
                "components": {
                    "groups": groups_result.get("status", "unknown"),
                    "summaries": summaries_result.get("status", "unknown"),
                    "configuration": config_result.get("status", "unknown")
                },
                "data_counts": {
                    "groups": len(groups_data),
                    "summaries": len(summaries_data),
                    "config_keys": len(config_data)
                }
            }
            
            logger.info("Full system backup completed successfully", **result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "backup_type": "full_system"
            }
            logger.error("Full system backup failed", **error_result)
            return error_result
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """
        PT-BR:
        Remove backups antigos baseado na configuração de retenção.
        
        Retorna:
            Dict: Resultado da limpeza
            
        EN:
        Remove old backups based on retention configuration.
        
        Returns:
            Dict: Cleanup result
        """
        if not self.config.backup_enabled:
            return {"status": "disabled", "message": "Backup is disabled"}
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.backup_retention_days)
            deleted_files = []
            total_size_freed = 0
            
            for file_path in self.backup_path.glob("*_backup_*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        file_size = self._get_file_size_mb(file_path)
                        deleted_files.append({
                            "filename": file_path.name,
                            "size_mb": round(file_size, 2),
                            "created": file_mtime.isoformat()
                        })
                        
                        total_size_freed += file_size
                        file_path.unlink()
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "retention_days": self.config.backup_retention_days,
                "files_deleted": len(deleted_files),
                "space_freed_mb": round(total_size_freed, 2),
                "deleted_files": deleted_files
            }
            
            logger.info("Backup cleanup completed", **result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Backup cleanup failed", **error_result)
            return error_result
    
    def list_backups(self) -> Dict[str, Any]:
        """
        PT-BR:
        Lista todos os backups disponíveis.
        
        Retorna:
            Dict: Lista de backups
            
        EN:
        List all available backups.
        
        Returns:
            Dict: List of backups
        """
        try:
            backups = []
            total_size = 0
            
            for file_path in sorted(self.backup_path.glob("*_backup_*")):
                if file_path.is_file():
                    file_size = self._get_file_size_mb(file_path)
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # Extrair tipo de backup do nome do arquivo
                    name_parts = file_path.stem.split('_')
                    backup_type = name_parts[0] if name_parts else "unknown"
                    
                    backup_info = {
                        "filename": file_path.name,
                        "type": backup_type,
                        "size_mb": round(file_size, 2),
                        "created": file_mtime.isoformat(),
                        "age_days": (datetime.now() - file_mtime).days,
                        "format": file_path.suffix[1:],  # Remove o ponto
                        "path": str(file_path)
                    }
                    
                    backups.append(backup_info)
                    total_size += file_size
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "backup_directory": str(self.backup_path),
                "total_backups": len(backups),
                "total_size_mb": round(total_size, 2),
                "retention_days": self.config.backup_retention_days,
                "backups": backups
            }
            
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Failed to list backups", **error_result)
            return error_result
    
    def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        PT-BR:
        Restaura dados de um arquivo de backup.
        
        Parâmetros:
            backup_filename: Nome do arquivo de backup
            
        Retorna:
            Dict: Dados restaurados
            
        EN:
        Restore data from a backup file.
        
        Parameters:
            backup_filename: Backup filename
            
        Returns:
            Dict: Restored data
        """
        try:
            backup_path = self.backup_path / backup_filename
            
            if not backup_path.exists():
                return {
                    "status": "error",
                    "error": f"Backup file not found: {backup_filename}"
                }
            
            # Verificar se é arquivo comprimido
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Assumir que há um arquivo JSON principal
                    json_files = [f for f in zipf.namelist() if f.endswith('.json')]
                    if not json_files:
                        return {
                            "status": "error",
                            "error": "No JSON file found in zip archive"
                        }
                    
                    with zipf.open(json_files[0]) as f:
                        data = json.load(f)
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "backup_filename": backup_filename,
                "data_type": data.get("metadata", {}).get("data_type", "unknown"),
                "backup_timestamp": data.get("metadata", {}).get("timestamp", "unknown"),
                "data": data
            }
            
            logger.info("Backup restored successfully", filename=backup_filename)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "backup_filename": backup_filename
            }
            logger.error("Backup restore failed", **error_result)
            return error_result


# Instância global
backup_manager = BackupManager()
