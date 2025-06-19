#!/usr/bin/env python3
"""
Script de Migração para Nova Estrutura
Migration Script for New Structure

PT-BR:
Este script ajuda a migrar gradualmente da estrutura antiga
para a nova estrutura organizada.

EN:
This script helps gradually migrate from the old structure
to the new organized structure.
"""

import os
import shutil
import sys
from pathlib import Path


class StructureMigrator:
    """
    Migrador de estrutura do projeto
    Project structure migrator
    """
    
    def __init__(self, project_root: str):
        """
        Inicializa o migrador
        Initializes the migrator
        """
        self.project_root = Path(project_root)
        self.old_src = self.project_root / "src" / "whatsapp_manager"
        self.new_src = self.project_root / "src_clean" / "whatsapp_manager"
        
        print(f"🏗️ Migrador de Estrutura - WhatsApp Manager")
        print(f"📁 Diretório do projeto: {self.project_root}")
        print(f"📁 Estrutura antiga: {self.old_src}")
        print(f"📁 Estrutura nova: {self.new_src}")
    
    def validate_environment(self) -> bool:
        """
        Valida se o ambiente está pronto para migração
        Validates if environment is ready for migration
        """
        print("\n🔍 Validando ambiente...")
        
        # Verificar se estrutura antiga existe
        if not self.old_src.exists():
            print(f"❌ Estrutura antiga não encontrada: {self.old_src}")
            return False
        
        # Verificar se estrutura nova foi criada
        if not self.new_src.exists():
            print(f"❌ Estrutura nova não encontrada: {self.new_src}")
            print("💡 Execute primeiro a criação da nova estrutura")
            return False
        
        print("✅ Ambiente validado com sucesso")
        return True
    
    def backup_current_structure(self) -> bool:
        """
        Cria backup da estrutura atual
        Creates backup of current structure
        """
        print("\n💾 Criando backup da estrutura atual...")
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.project_root / f"backup_migration_{timestamp}"
            
            # Copiar estrutura antiga
            shutil.copytree(self.old_src, backup_dir / "whatsapp_manager_old")
            
            print(f"✅ Backup criado em: {backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    
    def compare_structures(self):
        """
        Compara estruturas antiga e nova
        Compares old and new structures
        """
        print("\n📊 Comparando estruturas...")
        
        print("\n📁 Estrutura Antiga:")
        self._print_tree(self.old_src, prefix="  ")
        
        print("\n📁 Estrutura Nova:")
        self._print_tree(self.new_src, prefix="  ")
    
    def analyze_migration_needs(self) -> dict:
        """
        Analisa o que precisa ser migrado
        Analyzes what needs to be migrated
        """
        print("\n🔍 Analisando necessidades de migração...")
        
        migration_map = {}
        
        # Analisar arquivos da estrutura antiga
        for file_path in self.old_src.rglob("*.py"):
            relative_path = file_path.relative_to(self.old_src)
            
            # Determinar destino na nova estrutura
            destination = self._determine_destination(relative_path)
            
            migration_map[str(relative_path)] = destination
        
        # Mostrar mapeamento
        print("\n📋 Mapeamento de Migração:")
        for source, dest in migration_map.items():
            status = "✅" if dest else "❓"
            dest_str = dest if dest else "A DEFINIR"
            print(f"  {status} {source} → {dest_str}")
        
        return migration_map
    
    def _determine_destination(self, relative_path: Path) -> str:
        """
        Determina destino de um arquivo na nova estrutura
        Determines destination of a file in new structure
        """
        file_name = relative_path.name
        
        # Mapeamento baseado em nome do arquivo
        if file_name == "group.py":
            return "core/models/group.py"
        elif file_name == "group_controller.py":
            return "core/controllers/group_controller.py"
        elif file_name == "message_sandeco.py":
            return "core/models/message.py (requires refactoring)"
        elif file_name == "send_sandeco.py":
            return "infrastructure/messaging/message_sender.py (requires refactoring)"
        elif file_name == "summary.py":
            return "core/services/summary_service.py (requires refactoring)"
        elif file_name == "summary_crew.py":
            return "infrastructure/ai/summary_crew.py"
        elif file_name == "task_scheduler.py":
            return "infrastructure/scheduling/task_scheduler.py"
        elif "util" in file_name:
            return f"shared/utils/{file_name}"
        elif relative_path.parts[0] == "ui":
            return f"presentation/web/{'/'.join(relative_path.parts[1:])}"
        else:
            return "TO_BE_DEFINED"
    
    def generate_migration_plan(self):
        """
        Gera plano detalhado de migração
        Generates detailed migration plan
        """
        print("\n📋 Gerando Plano de Migração...")
        
        plan = """
# 🗺️ PLANO DE MIGRAÇÃO - WHATSAPP MANAGER

## 📋 FASES DA MIGRAÇÃO

### Fase 1: Preparação ✅
- [x] Criar nova estrutura de diretórios
- [x] Definir mapeamento de arquivos
- [x] Criar documentação da nova estrutura

### Fase 2: Migração Core 🔄
- [ ] Migrar models (Group, Message)
- [ ] Migrar controllers (GroupController)
- [ ] Migrar services (SummaryService, MessageService)
- [ ] Atualizar imports e dependências

### Fase 3: Migração Infrastructure 📋
- [ ] Migrar API clients (EvolutionClient)
- [ ] Migrar message sending (MessageSender)
- [ ] Migrar persistence (GroupRepository)
- [ ] Migrar scheduling (TaskScheduler)

### Fase 4: Migração Presentation 📋
- [ ] Migrar interface Streamlit
- [ ] Atualizar paths e imports
- [ ] Testar interface atualizada

### Fase 5: Finalização 📋
- [ ] Executar testes completos
- [ ] Atualizar documentação
- [ ] Remover estrutura antiga
- [ ] Deploy da nova versão

## 🔧 COMANDOS DE MIGRAÇÃO

```bash
# 1. Executar análise
python migrate_structure.py --analyze

# 2. Criar backup
python migrate_structure.py --backup

# 3. Migrar fase por fase
python migrate_structure.py --migrate core
python migrate_structure.py --migrate infrastructure
python migrate_structure.py --migrate presentation

# 4. Validar migração
python migrate_structure.py --validate
```

## ⚠️ CUIDADOS ESPECIAIS

1. **Testes**: Executar testes após cada fase
2. **Backup**: Manter backups de segurança
3. **Imports**: Atualizar todos os imports
4. **Configurações**: Verificar paths de arquivos
5. **Dependências**: Validar injeção de dependências
"""
        
        plan_file = self.project_root / "MIGRATION_PLAN.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan)
        
        print(f"✅ Plano salvo em: {plan_file}")
    
    def _print_tree(self, path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
        """
        Imprime árvore de diretórios
        Prints directory tree
        """
        if current_depth >= max_depth:
            return
        
        if not path.exists():
            print(f"{prefix}❌ {path.name} (não existe)")
            return
        
        items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            if item.is_dir():
                print(f"{prefix}{current_prefix}📁 {item.name}/")
                self._print_tree(item, next_prefix, max_depth, current_depth + 1)
            else:
                icon = "🐍" if item.suffix == ".py" else "📄"
                print(f"{prefix}{current_prefix}{icon} {item.name}")
    
    def interactive_migration(self):
        """
        Migração interativa guiada
        Interactive guided migration
        """
        print("\n🎯 Migração Interativa")
        print("=" * 50)
        
        while True:
            print("\n📋 Opções disponíveis:")
            print("1. 🔍 Analisar estruturas")
            print("2. 💾 Criar backup")
            print("3. 📊 Comparar estruturas")
            print("4. 🗺️ Gerar plano de migração")
            print("5. 🚪 Sair")
            
            choice = input("\n➡️ Escolha uma opção (1-5): ").strip()
            
            if choice == "1":
                if self.validate_environment():
                    self.analyze_migration_needs()
            elif choice == "2":
                self.backup_current_structure()
            elif choice == "3":
                self.compare_structures()
            elif choice == "4":
                self.generate_migration_plan()
            elif choice == "5":
                print("\n👋 Finalizando migração...")
                break
            else:
                print("❌ Opção inválida!")


def main():
    """
    Função principal
    Main function
    """
    print("🏗️ MIGRADOR DE ESTRUTURA - WHATSAPP MANAGER")
    print("=" * 50)
    
    # Obter diretório do projeto
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    # Inicializar migrador
    migrator = StructureMigrator(str(project_root))
    
    # Executar migração interativa
    migrator.interactive_migration()


if __name__ == "__main__":
    main()
