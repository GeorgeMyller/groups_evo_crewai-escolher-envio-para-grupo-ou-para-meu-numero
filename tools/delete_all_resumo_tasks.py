#!/usr/bin/env python3
"""
Script para excluir todas as tarefas ResumoGrupo_ agendadas no sistema macOS
"""

import os
import sys
import subprocess
import platform

# Adiciona o diretório src ao path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from whatsapp_manager.utils.task_scheduler import TaskScheduled

def get_resumo_tasks():
    """Lista todas as tarefas ResumoGrupo_ no sistema"""
    if platform.system() != "Darwin":
        print("Este script é específico para macOS")
        return []
    
    try:
        # Lista todas as tarefas do launchctl
        result = subprocess.run(['launchctl', 'list'], 
                              capture_output=True, text=True, check=True)
        
        tasks = []
        for line in result.stdout.split('\n'):
            if 'ResumoGrupo_' in line:
                # Extrai o nome da tarefa da linha
                parts = line.split()
                if len(parts) >= 3:
                    task_name = parts[2]  # O nome da tarefa está na terceira coluna
                    tasks.append(task_name)
        
        return tasks
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar tarefas: {e}")
        return []

def delete_task_manually(task_name):
    """Remove uma tarefa manualmente usando comandos do sistema"""
    try:
        print(f"Removendo tarefa: {task_name}")
        
        # Para a tarefa se estiver rodando
        subprocess.run(['launchctl', 'stop', task_name], 
                      capture_output=True, check=False)
        
        # Remove a tarefa do launchctl
        subprocess.run(['launchctl', 'remove', task_name], 
                      capture_output=True, check=False)
        
        # Remove o arquivo plist se existir
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{task_name}.plist")
        if os.path.exists(plist_path):
            os.remove(plist_path)
            print(f"  ✓ Arquivo plist removido: {plist_path}")
        
        print(f"  ✓ Tarefa {task_name} removida com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao remover {task_name}: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 Procurando tarefas ResumoGrupo_...")
    
    tasks = get_resumo_tasks()
    
    if not tasks:
        print("✅ Nenhuma tarefa ResumoGrupo_ encontrada!")
        return
    
    print(f"📋 Encontradas {len(tasks)} tarefas:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task}")
    
    print("\n⚠️  Você deseja excluir TODAS essas tarefas?")
    choice = input("Digite 's' para confirmar ou qualquer outra tecla para cancelar: ").strip().lower()
    
    if choice != 's':
        print("❌ Operação cancelada.")
        return
    
    print("\n🗑️  Iniciando remoção das tarefas...")
    
    success_count = 0
    failed_count = 0
    
    for task in tasks:
        if delete_task_manually(task):
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\n📊 Resultado:")
    print(f"  ✅ Removidas com sucesso: {success_count}")
    print(f"  ❌ Falharam: {failed_count}")
    
    if success_count > 0:
        print("\n🔍 Verificando se ainda há tarefas...")
        remaining_tasks = get_resumo_tasks()
        if remaining_tasks:
            print(f"⚠️  Ainda restam {len(remaining_tasks)} tarefas:")
            for task in remaining_tasks:
                print(f"  - {task}")
        else:
            print("✅ Todas as tarefas ResumoGrupo_ foram removidas!")

if __name__ == "__main__":
    main()
