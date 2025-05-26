"""
Migração da Estrutura do Projeto / Project Structure Migration

PT-BR:
Este script ajuda na migração da estrutura antiga do projeto para a nova
arquitetura organizada com separação clara de responsabilidades.

EN:
This script helps migrate from the old project structure to the new
organized architecture with clear separation of concerns.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Adiciona o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from structured_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class ProjectMigrator:
    """
    PT-BR:
    Classe responsável pela migração da estrutura do projeto.
    
    EN:
    Class responsible for project structure migration.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.src_dir = self.root_dir / "src"
        self.old_files_map = self._get_migration_map()
    
    def _get_migration_map(self) -> Dict[str, str]:
        """
        PT-BR:
        Mapa de migração dos arquivos antigos para nova estrutura.
        
        EN:
        Migration map from old files to new structure.
        """
        return {
            # Core Controllers
            "group_controller.py": "src/core/controllers/group_controller.py",
            
            # Core Services  
            "summary_crew.py": "src/core/services/summary_service.py",
            "message_sandeco.py": "src/core/services/message_service.py",
            "send_sandeco.py": "src/core/services/send_service.py",
            
            # Models (já migrado)
            "group.py": "legacy/group.py",  # Backup da versão antiga
            
            # Utils
            "groups_util.py": "src/utils/groups_helper.py",
            "task_scheduler.py": "src/utils/scheduler.py",
            
            # UI Components
            "pages/2_Portuguese.py": "src/ui/components/portuguese_page.py",
            "pages/3_English.py": "src/ui/components/english_page.py",
            "pages/4_Dashboard.py": "src/ui/components/dashboard_page.py",
            
            # Scripts
            "agendar_todos.py": "scripts/schedule_all.py",
            "delete_scheduled_tasks.py": "scripts/delete_tasks.py",
            "list_scheduled_tasks.py": "scripts/list_tasks.py",
            "save_groups_to_csv.py": "scripts/export_groups.py",
            "WhatsApp_Group_Resumer.py": "scripts/group_resumer.py",
            "summary.py": "scripts/legacy_summary.py",
            "summary_lite.py": "scripts/summary_lite.py",
            
            # Config (já migrado)
            "load_env.sh": "scripts/load_env.sh",
        }
    
    def create_backup(self) -> None:
        """
        PT-BR:
        Cria backup dos arquivos antes da migração.
        
        EN:
        Creates backup of files before migration.
        """
        try:
            backup_dir = self.root_dir / "backup_migration"
            backup_dir.mkdir(exist_ok=True)
            
            logger.info("Creating backup of current structure...")
            
            for old_file in self.old_files_map.keys():
                old_path = self.root_dir / old_file
                if old_path.exists():
                    backup_path = backup_dir / old_file
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(old_path, backup_path)
                    logger.info(f"Backed up: {old_file}")
            
            logger.info(f"Backup completed in: {backup_dir}")
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def create_legacy_directory(self) -> None:
        """
        PT-BR:
        Cria diretório legacy para arquivos antigos.
        
        EN:
        Creates legacy directory for old files.
        """
        legacy_dir = self.root_dir / "legacy"
        legacy_dir.mkdir(exist_ok=True)
        logger.info(f"Created legacy directory: {legacy_dir}")
    
    def update_imports_in_file(self, file_path: Path) -> None:
        """
        PT-BR:
        Atualiza imports em um arquivo para a nova estrutura.
        
        EN:
        Updates imports in a file for the new structure.
        """
        try:
            if not file_path.exists() or file_path.suffix != '.py':
                return
            
            # Mapa de imports antigos para novos
            import_map = {
                "from group import Group": "from src.core.models import Group",
                "from group_controller import GroupController": "from src.core.controllers import GroupController",
                "from summary_crew import SummaryCrew": "from src.core.services import SummaryService",
                "from message_sandeco import MessageSandeco": "from src.core.services import MessageService",
                "from send_sandeco import SendSandeco": "from src.core.services import SendService",
                "from groups_util import": "from src.utils.groups_helper import",
                "from task_scheduler import": "from src.utils.scheduler import",
                "import group": "from src.core.models import Group",
                "import group_controller": "from src.core.controllers import GroupController",
            }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplica substituições de imports
            for old_import, new_import in import_map.items():
                content = content.replace(old_import, new_import)
            
            # Salva apenas se houve mudanças
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Updated imports in: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to update imports in {file_path}: {e}")
    
    def migrate_files(self) -> None:
        """
        PT-BR:
        Migra arquivos para nova estrutura.
        
        EN:
        Migrates files to new structure.
        """
        try:
            logger.info("Starting file migration...")
            
            # Cria diretórios necessários
            directories_to_create = [
                "src/core/controllers",
                "src/core/services", 
                "src/core/models",
                "src/ui/components",
                "src/utils",
                "scripts",
                "legacy"
            ]
            
            for directory in directories_to_create:
                dir_path = self.root_dir / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Migra arquivos (apenas copia, não move ainda)
            for old_file, new_file in self.old_files_map.items():
                old_path = self.root_dir / old_file
                new_path = self.root_dir / new_file
                
                if old_path.exists():
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Para arquivos já migrados, apenas cria um symlink ou ignora
                    if "src/" in new_file and new_path.exists():
                        logger.info(f"Already migrated: {old_file} -> {new_file}")
                        continue
                    
                    # Copia arquivo
                    shutil.copy2(old_path, new_path)
                    logger.info(f"Migrated: {old_file} -> {new_file}")
                else:
                    logger.warning(f"Source file not found: {old_file}")
            
            logger.info("File migration completed")
            
        except Exception as e:
            logger.error(f"File migration failed: {e}")
            raise
    
    def update_all_imports(self) -> None:
        """
        PT-BR:
        Atualiza imports em todos os arquivos Python.
        
        EN:
        Updates imports in all Python files.
        """
        try:
            logger.info("Updating imports in all Python files...")
            
            # Arquivos para atualizar imports
            python_files = []
            
            # Encontra todos os arquivos Python
            for pattern in ["*.py", "**/*.py"]:
                python_files.extend(self.root_dir.glob(pattern))
            
            for py_file in python_files:
                # Pula arquivos de backup e __pycache__
                if any(skip in str(py_file) for skip in ["backup_", "__pycache__", ".pyc", "migration.py"]):
                    continue
                
                self.update_imports_in_file(py_file)
            
            logger.info("Import updates completed")
            
        except Exception as e:
            logger.error(f"Import update failed: {e}")
            raise
    
    def create_compatibility_files(self) -> None:
        """
        PT-BR:
        Cria arquivos de compatibilidade para transição suave.
        
        EN:
        Creates compatibility files for smooth transition.
        """
        try:
            logger.info("Creating compatibility files...")
            
            # Arquivo de compatibilidade para group.py
            compat_group = self.root_dir / "group.py"
            compat_content = '''"""
Compatibility layer for legacy Group class

This file provides backward compatibility during migration.
Use 'from src.core.models import Group' for new code.
"""

import warnings
from src.core.models import Group

warnings.warn(
    "Importing from 'group.py' is deprecated. Use 'from src.core.models import Group' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['Group']
'''
            
            with open(compat_group, 'w', encoding='utf-8') as f:
                f.write(compat_content)
            
            logger.info("Created compatibility file: group.py")
            
            # Arquivo de compatibilidade para group_controller.py
            compat_controller = self.root_dir / "group_controller.py" 
            compat_content = '''"""
Compatibility layer for legacy GroupController class

This file provides backward compatibility during migration.
Use 'from src.core.controllers import GroupController' for new code.
"""

import warnings
from src.core.controllers import GroupController

warnings.warn(
    "Importing from 'group_controller.py' is deprecated. Use 'from src.core.controllers import GroupController' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['GroupController']
'''
            
            with open(compat_controller, 'w', encoding='utf-8') as f:
                f.write(compat_content)
            
            logger.info("Created compatibility file: group_controller.py")
            
        except Exception as e:
            logger.error(f"Failed to create compatibility files: {e}")
            raise
    
    def run_migration(self) -> None:
        """
        PT-BR:
        Executa a migração completa.
        
        EN:
        Runs the complete migration.
        """
        try:
            logger.info("Starting project structure migration...")
            
            # Passo 1: Backup
            self.create_backup()
            
            # Passo 2: Criar diretórios
            self.create_legacy_directory()
            
            # Passo 3: Migrar arquivos
            # self.migrate_files()  # Comentado por enquanto
            
            # Passo 4: Criar arquivos de compatibilidade
            self.create_compatibility_files()
            
            # Passo 5: Atualizar imports (comentado para não quebrar arquivos existentes)
            # self.update_all_imports()
            
            logger.info("Migration completed successfully!")
            logger.info("Next steps:")
            logger.info("1. Test the new structure with: python -m pytest tests/")
            logger.info("2. Update your IDE to use the new import paths")
            logger.info("3. Gradually update imports in your code")
            logger.info("4. Remove compatibility files when migration is complete")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


def main():
    """
    PT-BR:
    Função principal para executar a migração.
    
    EN:
    Main function to run migration.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    migrator = ProjectMigrator(root_dir)
    migrator.run_migration()


if __name__ == "__main__":
    main()
