#!/usr/bin/env python3
"""
🔧 CORRETOR COMPLETO DA ESTRUTURA ORGANIZADA
============================================

Este script corrige todos os problemas identificados na estrutura reorganizada:
1. ❌ Caminhos incorretos para CSV
2. ❌ Imports quebrados nas páginas UI
3. ❌ Imports quebrados nos scripts
4. ✅ Validação da estrutura final

Uso: python fix_organized_structure.py
"""

import os
import sys
import shutil
from pathlib import Path

# Configuração do projeto
PROJECT_ROOT = Path(__file__).parent.absolute()
print(f"🔧 Projeto Root: {PROJECT_ROOT}")

class OrganizedStructureFixer:
    """Corrige problemas da estrutura organizada do projeto"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.src_dir = self.project_root / "src"
        self.whatsapp_manager_dir = self.src_dir / "whatsapp_manager"
        self.scripts_dir = self.project_root / "scripts"
        self.data_dir = self.project_root / "data"
        
        # Arquivos críticos
        self.group_csv_root = self.project_root / "group_summary.csv"
        self.group_csv_data = self.data_dir / "group_summary.csv"
        
        self.problems_found = []
        self.fixes_applied = []
    
    def analyze_structure(self):
        """Analisa a estrutura atual e identifica problemas"""
        print("\n📊 ANÁLISE DA ESTRUTURA ATUAL")
        print("=" * 50)
        
        # 1. Verificar arquivos CSV
        print("\n1️⃣ VERIFICANDO ARQUIVOS CSV:")
        if self.group_csv_root.exists():
            print(f"   ✅ CSV na raiz: {self.group_csv_root}")
        else:
            print(f"   ❌ CSV na raiz não encontrado: {self.group_csv_root}")
            self.problems_found.append("CSV na raiz inexistente")
        
        if not self.data_dir.exists():
            print(f"   ❌ Diretório data não existe: {self.data_dir}")
            self.problems_found.append("Diretório data inexistente")
        elif self.group_csv_data.exists():
            print(f"   ✅ CSV em data: {self.group_csv_data}")
        else:
            print(f"   ❌ CSV em data não encontrado: {self.group_csv_data}")
            self.problems_found.append("CSV em data inexistente")
        
        # 2. Verificar estrutura de diretórios
        print("\n2️⃣ VERIFICANDO ESTRUTURA DE DIRETÓRIOS:")
        required_dirs = [
            self.src_dir,
            self.whatsapp_manager_dir,
            self.whatsapp_manager_dir / "core",
            self.whatsapp_manager_dir / "ui" / "pages",
            self.whatsapp_manager_dir / "utils",
            self.scripts_dir
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"   ✅ {dir_path.relative_to(self.project_root)}")
            else:
                print(f"   ❌ {dir_path.relative_to(self.project_root)}")
                self.problems_found.append(f"Diretório ausente: {dir_path}")
        
        # 3. Verificar arquivos críticos
        print("\n3️⃣ VERIFICANDO ARQUIVOS CRÍTICOS:")
        critical_files = [
            self.whatsapp_manager_dir / "core" / "group_controller.py",
            self.whatsapp_manager_dir / "core" / "group.py",
            self.whatsapp_manager_dir / "core" / "summary.py",
            self.whatsapp_manager_dir / "core" / "send_sandeco.py",
            self.whatsapp_manager_dir / "utils" / "task_scheduler.py",
            self.whatsapp_manager_dir / "utils" / "groups_util.py",
            self.whatsapp_manager_dir / "ui" / "main_app.py",
            self.whatsapp_manager_dir / "ui" / "pages" / "2_Portuguese.py",
            self.whatsapp_manager_dir / "ui" / "pages" / "3_English.py",
            self.scripts_dir / "agendar_todos.py",
            self.scripts_dir / "delete_scheduled_tasks.py"
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                print(f"   ✅ {file_path.relative_to(self.project_root)}")
            else:
                print(f"   ❌ {file_path.relative_to(self.project_root)}")
                self.problems_found.append(f"Arquivo ausente: {file_path}")
        
        # Resumo da análise
        print(f"\n📈 RESUMO: {len(self.problems_found)} problemas encontrados")
        return len(self.problems_found) == 0
    
    def fix_csv_structure(self):
        """Corrige problemas com arquivos CSV"""
        print("\n🔧 CORRIGINDO ESTRUTURA CSV")
        print("=" * 40)
        
        # Criar diretório data se não existir
        if not self.data_dir.exists():
            self.data_dir.mkdir(exist_ok=True)
            print(f"   ✅ Criado diretório: {self.data_dir}")
            self.fixes_applied.append("Diretório data criado")
        
        # Se CSV existe na raiz mas não em data, copiar
        if self.group_csv_root.exists() and not self.group_csv_data.exists():
            shutil.copy2(self.group_csv_root, self.group_csv_data)
            print(f"   ✅ CSV copiado: raiz → data/")
            self.fixes_applied.append("CSV copiado para data/")
        
        # Se CSV não existe em lugar nenhum, criar um básico
        if not self.group_csv_root.exists() and not self.group_csv_data.exists():
            csv_content = """group_id,group_name,total_messages,min_messages_summary,summary_scheduled,last_summary_date,send_to_group,my_number
example_group,Grupo Exemplo,0,10,False,,False,5511999999999
"""
            self.group_csv_data.write_text(csv_content)
            shutil.copy2(self.group_csv_data, self.group_csv_root)
            print(f"   ✅ CSV básico criado em ambos os locais")
            self.fixes_applied.append("CSV básico criado")
    
    def fix_ui_imports(self):
        """Corrige imports quebrados nas páginas UI"""
        print("\n🔧 CORRIGINDO IMPORTS DAS PÁGINAS UI")
        print("=" * 45)
        
        ui_pages = [
            self.whatsapp_manager_dir / "ui" / "pages" / "2_Portuguese.py",
            self.whatsapp_manager_dir / "ui" / "pages" / "3_English.py"
        ]
        
        for page_file in ui_pages:
            if not page_file.exists():
                print(f"   ❌ Arquivo não encontrado: {page_file}")
                continue
            
            # Ler conteúdo atual
            content = page_file.read_text(encoding='utf-8')
            
            # Encontrar e corrigir a seção de imports
            lines = content.split('\n')
            fixed_lines = []
            import_section_started = False
            import_section_fixed = False
            
            for i, line in enumerate(lines):
                # Detectar início da seção de imports locais
                if "# Local application/library imports" in line or "# Define Project Root" in line:
                    import_section_started = True
                    
                    # Inserir imports corrigidos
                    if not import_section_fixed:
                        fixed_lines.extend([
                            "# Local application/library imports",
                            "# Define Project Root assuming this file is in src/whatsapp_manager/ui/pages/",
                            "# Navigate four levels up to reach the project root.",
                            "PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))",
                            "",
                            "# Add src to Python path for imports",
                            "import sys",
                            "if PROJECT_ROOT not in sys.path:",
                            "    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))",
                            "",
                            "# Import local modules",
                            "from whatsapp_manager.core.group_controller import GroupController",
                            "from whatsapp_manager.utils.groups_util import GroupUtils",
                            "from whatsapp_manager.utils.task_scheduler import TaskScheduled",
                            "from whatsapp_manager.core.send_sandeco import SendSandeco",
                            ""
                        ])
                        import_section_fixed = True
                        
                        # Pular linhas até o final da seção de imports
                        while i < len(lines) and not lines[i].startswith("# ---"):
                            i += 1
                        if i < len(lines):
                            fixed_lines.append(lines[i])  # Adicionar a linha "# ---"
                        continue
                
                # Se não estamos na seção de imports, manter linha original
                if not import_section_started or import_section_fixed:
                    fixed_lines.append(line)
            
            # Escrever arquivo corrigido se houve mudanças
            fixed_content = '\n'.join(fixed_lines)
            if fixed_content != content:
                page_file.write_text(fixed_content, encoding='utf-8')
                print(f"   ✅ Imports corrigidos: {page_file.name}")
                self.fixes_applied.append(f"Imports UI corrigidos: {page_file.name}")
            else:
                print(f"   ℹ️  Imports já corretos: {page_file.name}")
    
    def fix_script_imports(self):
        """Corrige imports quebrados nos scripts"""
        print("\n🔧 CORRIGINDO IMPORTS DOS SCRIPTS")
        print("=" * 42)
        
        # Corrigir agendar_todos.py
        agendar_file = self.scripts_dir / "agendar_todos.py"
        if agendar_file.exists():
            content = agendar_file.read_text(encoding='utf-8')
            
            # Substituir referências incorretas de paths
            content = content.replace(
                'group_info_csv_path = os.path.join(PROJECT_ROOT, "data", "group_info.csv")',
                'group_info_csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")'
            )
            
            # Adicionar fallback para CSV
            if 'if not os.path.exists(group_info_csv_path):' in content:
                content = content.replace(
                    'if not os.path.exists(group_info_csv_path):',
                    '''# Try data directory first, then root
group_info_csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
if not os.path.exists(group_info_csv_path):
    group_info_csv_path = os.path.join(PROJECT_ROOT, "group_summary.csv")

if not os.path.exists(group_info_csv_path):'''
                )
            
            agendar_file.write_text(content, encoding='utf-8')
            print(f"   ✅ Script corrigido: agendar_todos.py")
            self.fixes_applied.append("Script agendar_todos.py corrigido")
        
        # Corrigir delete_scheduled_tasks.py
        delete_file = self.scripts_dir / "delete_scheduled_tasks.py"
        if delete_file.exists():
            content = delete_file.read_text(encoding='utf-8')
            
            # Corrigir path do CSV com fallback
            if 'GROUP_SUMMARY_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")' in content:
                content = content.replace(
                    'GROUP_SUMMARY_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")',
                    '''# Try data directory first, then root
GROUP_SUMMARY_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
if not os.path.exists(GROUP_SUMMARY_CSV_PATH):
    GROUP_SUMMARY_CSV_PATH = os.path.join(PROJECT_ROOT, "group_summary.csv")'''
                )
            
            delete_file.write_text(content, encoding='utf-8')
            print(f"   ✅ Script corrigido: delete_scheduled_tasks.py")
            self.fixes_applied.append("Script delete_scheduled_tasks.py corrigido")
    
    def fix_core_modules(self):
        """Corrige problemas nos módulos core"""
        print("\n🔧 CORRIGINDO MÓDULOS CORE")
        print("=" * 35)
        
        # Corrigir group_controller.py para usar fallback de CSV
        controller_file = self.whatsapp_manager_dir / "core" / "group_controller.py"
        if controller_file.exists():
            content = controller_file.read_text(encoding='utf-8')
            
            # Verificar se já tem o fallback implementado
            if 'csv_root_path' in content and 'if os.path.exists(csv_data_path):' not in content:
                # Encontrar a seção onde os paths são definidos e adicionar lógica de fallback
                lines = content.split('\n')
                fixed_lines = []
                
                for i, line in enumerate(lines):
                    fixed_lines.append(line)
                    
                    # Adicionar lógica de fallback após definir os paths
                    if 'csv_root_path = os.path.join(PROJECT_ROOT, "group_summary.csv")' in line:
                        fixed_lines.extend([
                            "",
                            "        # Use data directory if available, otherwise use root",
                            "        if os.path.exists(csv_data_path):",
                            "            return csv_data_path",
                            "        elif os.path.exists(csv_root_path):",
                            "            return csv_root_path",
                            "        else:",
                            "            # Create in data directory if neither exists",
                            "            os.makedirs(data_dir, exist_ok=True)",
                            "            return csv_data_path"
                        ])
                        
                        # Pular até encontrar o próximo bloco de código
                        while i + 1 < len(lines) and not lines[i + 1].strip().startswith('return'):
                            i += 1
                        continue
                
                controller_file.write_text('\n'.join(fixed_lines), encoding='utf-8')
                print(f"   ✅ Fallback CSV adicionado: group_controller.py")
                self.fixes_applied.append("Fallback CSV em group_controller.py")
            else:
                print(f"   ℹ️  Fallback já implementado: group_controller.py")
    
    def validate_structure(self):
        """Valida se a estrutura está funcionando corretamente"""
        print("\n✅ VALIDAÇÃO DA ESTRUTURA CORRIGIDA")
        print("=" * 45)
        
        validation_passed = True
        
        # 1. Testar imports
        print("\n1️⃣ TESTANDO IMPORTS:")
        try:
            # Adicionar src ao Python path temporariamente
            sys.path.insert(0, str(self.src_dir))
            
            from whatsapp_manager.core.group_controller import GroupController
            from whatsapp_manager.utils.groups_util import GroupUtils
            from whatsapp_manager.utils.task_scheduler import TaskScheduled
            from whatsapp_manager.core.send_sandeco import SendSandeco
            
            print("   ✅ Todos os imports principais funcionando")
        except ImportError as e:
            print(f"   ❌ Erro de import: {e}")
            validation_passed = False
        finally:
            # Remover do path
            if str(self.src_dir) in sys.path:
                sys.path.remove(str(self.src_dir))
        
        # 2. Verificar paths CSV
        print("\n2️⃣ VERIFICANDO PATHS CSV:")
        if self.group_csv_data.exists() or self.group_csv_root.exists():
            print("   ✅ Pelo menos um CSV disponível")
        else:
            print("   ❌ Nenhum CSV encontrado")
            validation_passed = False
        
        # 3. Verificar estrutura de diretórios
        print("\n3️⃣ VERIFICANDO ESTRUTURA FINAL:")
        required_structure = {
            "src/whatsapp_manager/core/": ["group_controller.py", "group.py", "summary.py", "send_sandeco.py"],
            "src/whatsapp_manager/ui/": ["main_app.py"],
            "src/whatsapp_manager/ui/pages/": ["2_Portuguese.py", "3_English.py"],
            "src/whatsapp_manager/utils/": ["task_scheduler.py", "groups_util.py"],
            "scripts/": ["agendar_todos.py", "delete_scheduled_tasks.py"]
        }
        
        for dir_path, files in required_structure.items():
            full_dir = self.project_root / dir_path
            if full_dir.exists():
                print(f"   ✅ {dir_path}")
                for file_name in files:
                    file_path = full_dir / file_name
                    if file_path.exists():
                        print(f"      ✅ {file_name}")
                    else:
                        print(f"      ❌ {file_name}")
                        validation_passed = False
            else:
                print(f"   ❌ {dir_path}")
                validation_passed = False
        
        return validation_passed
    
    def run_complete_fix(self):
        """Executa todas as correções necessárias"""
        print("🚀 INICIANDO CORREÇÃO COMPLETA DA ESTRUTURA ORGANIZADA")
        print("=" * 65)
        
        # 1. Análise inicial
        structure_ok = self.analyze_structure()
        
        if structure_ok:
            print("\n🎉 Estrutura já está correta!")
            return True
        
        # 2. Aplicar correções
        print(f"\n🔧 Aplicando {len(self.problems_found)} correções...")
        
        self.fix_csv_structure()
        self.fix_ui_imports()
        self.fix_script_imports()
        self.fix_core_modules()
        
        # 3. Validação final
        if self.validate_structure():
            print("\n🎉 ESTRUTURA CORRIGIDA COM SUCESSO!")
            print("\n📋 CORREÇÕES APLICADAS:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("   1. Execute: uv run streamlit run src/whatsapp_manager/ui/main_app.py")
            print("   2. Teste as páginas Portuguese e English")
            print("   3. Execute os scripts em scripts/ para verificar funcionamento")
            print("   4. Verifique se o CSV está sendo lido corretamente")
            
            return True
        else:
            print("\n❌ ALGUMAS CORREÇÕES FALHARAM")
            print("   Verifique os logs acima para detalhes específicos")
            return False


def main():
    """Função principal"""
    fixer = OrganizedStructureFixer()
    success = fixer.run_complete_fix()
    
    if success:
        print("\n✅ Estrutura organizada corrigida e validada!")
        return 0
    else:
        print("\n❌ Correção incompleta. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    exit(main())
