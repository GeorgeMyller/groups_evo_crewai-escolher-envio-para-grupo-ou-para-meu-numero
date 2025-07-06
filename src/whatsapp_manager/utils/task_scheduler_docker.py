"""
Sistema de Agendamento de Tarefas para Docker / Docker Task Scheduling System

PT-BR:
Este módulo implementa um sistema simplificado de agendamento de tarefas 
específico para o ambiente Docker Linux. Funciona exclusivamente com cron.

EN:
This module implements a simplified task scheduling system 
specific for Docker Linux environment. Works exclusively with cron.
"""

import os
import subprocess
from datetime import datetime

class TaskScheduled:
    @staticmethod
    def validate_python_script(python_script_path):
        """
        PT-BR:
        Verifica se o script Python especificado existe no sistema.
        
        Parâmetros:
            python_script_path: Caminho do script a ser validado
            
        Raises:
            FileNotFoundError: Se o script não for encontrado

        EN:
        Validates if the specified Python script exists in the system.
        
        Parameters:
            python_script_path: Path to script to validate
            
        Raises:
            FileNotFoundError: If script is not found
        """
        if not os.path.exists(python_script_path):
            raise FileNotFoundError(f"Script Python não encontrado / Python script not found: '{python_script_path}'")

    @staticmethod
    def create_task(task_name, python_script_path, schedule_type='DAILY', date=None, time='22:00'):
        """
        PT-BR:
        Cria uma tarefa agendada no cron do Linux (Docker).
        
        Parâmetros:
            task_name: Nome da tarefa
            python_script_path: Caminho do script Python
            schedule_type: Tipo de agendamento ('DAILY' ou 'ONCE')
            date: Data para execução única (formato: YYYY-MM-DD)
            time: Horário de execução (formato: HH:MM)
            
        Raises:
            Exception: Para erros de agendamento

        EN:
        Creates a scheduled task in Linux cron (Docker).
        
        Parameters:
            task_name: Task name
            python_script_path: Python script path
            schedule_type: Schedule type ('DAILY' or 'ONCE')
            date: Date for one-time execution (format: YYYY-MM-DD)
            time: Execution time (format: HH:MM)
            
        Raises:
            Exception: For scheduling errors
        """
        TaskScheduled.validate_python_script(python_script_path)

        # No Docker, sempre usamos python3
        python_executable = "python3"
        
        # Comando que será executado pelo cron (usa o script load_env.sh)
        env_loader_script = "/usr/local/bin/load_env.sh"
        cron_command = f"{env_loader_script} {python_executable} {python_script_path} --task_name {task_name}"
        
        if schedule_type.upper() == 'ONCE' and date:
            # IMPORTANTE: Para execução "uma vez", convertemos para agendamento diário
            # pois o cron padrão não suporta anos específicos
            # O script summary.py deve verificar se já executou hoje
            hour, minute = time.split(':')
            command = f'(crontab -l 2>/dev/null ; echo "{minute} {hour} * * * {cron_command} # TASK_ID:{task_name}") | crontab -'
            print(f"AVISO: Agendamento 'ONCE' convertido para DAILY. Script deve verificar execução única.")
        else:  # DAILY
            hour, minute = time.split(':')
            command = f'(crontab -l 2>/dev/null ; echo "{minute} {hour} * * * {cron_command} # TASK_ID:{task_name}") | crontab -'

        try:
            subprocess.run(command, shell=True, check=True, text=True)
            print(f"Tarefa '{task_name}' criada com sucesso no cron do Docker!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar a tarefa: {e}")
            raise

    @staticmethod
    def delete_task(task_name):
        """
        PT-BR:
        Remove uma tarefa agendada do cron.
        
        Parâmetros:
            task_name: Nome da tarefa a ser removida
            
        Raises:
            Exception: Para erros na remoção

        EN:
        Removes a scheduled task from cron.
        
        Parameters:
            task_name: Name of task to remove
            
        Raises:
            Exception: For removal errors
        """
        # Remove a tarefa do crontab filtrando pela tag # TASK_ID:{task_name}
        command = f"crontab -l 2>/dev/null | grep -v '# TASK_ID:{task_name}' | crontab -"

        try:
            subprocess.run(command, shell=True, check=True, text=True)
            print(f"Tarefa '{task_name}' removida com sucesso do cron!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao remover a tarefa: {e}")
            raise

    @staticmethod
    def list_tasks():
        """
        PT-BR:
        Lista todas as tarefas agendadas no cron.
        
        Raises:
            Exception: Para erros na listagem

        EN:
        Lists all scheduled tasks in cron.
        
        Raises:
            Exception: For listing errors
        """
        command = "crontab -l 2>/dev/null"

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 TAREFAS AGENDADAS NO CRON:")
                print("=" * 50)
                if result.stdout.strip():
                    print(result.stdout)
                else:
                    print("Nenhuma tarefa agendada encontrada.")
            else:
                print("Nenhuma tarefa agendada encontrada.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao listar as tarefas: {e}")
            raise

    @staticmethod
    def list_project_tasks():
        """
        PT-BR:
        Lista apenas as tarefas relacionadas ao projeto WhatsApp Manager.
        
        Returns:
            list: Lista de tarefas do projeto com detalhes

        EN:
        Lists only tasks related to the WhatsApp Manager project.
        
        Returns:
            list: List of project tasks with details
        """
        project_tasks = []
        
        try:
            result = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '# TASK_ID:' in line and 'ResumoGrupo' in line:
                        # Extrai informações da linha do cron
                        parts = line.split('# TASK_ID:')
                        if len(parts) == 2:
                            task_name = parts[1].strip()
                            cron_schedule = parts[0].strip()
                            group_id = task_name.split('_')[1] if '_' in task_name else 'Unknown'
                            
                            project_tasks.append({
                                'label': task_name,
                                'group_id': group_id,
                                'schedule': cron_schedule,
                                'status': 'Agendado'
                            })
        except subprocess.CalledProcessError:
            pass  # Sem tarefas agendadas
        
        return project_tasks

    @staticmethod
    def print_project_tasks_summary():
        """
        PT-BR:
        Imprime um resumo formatado das tarefas do projeto.

        EN:
        Prints a formatted summary of project tasks.
        """
        tasks = TaskScheduled.list_project_tasks()
        
        if not tasks:
            print("❌ NENHUMA TAREFA DO PROJETO ENCONTRADA")
            print("   Verifique se você agendou alguma tarefa usando o sistema.")
            return
        
        print(f"📋 RESUMO DAS TAREFAS AGENDADAS ({len(tasks)} encontradas)")
        print("=" * 60)
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i:2d}. TAREFA: {task['label']}")
            print(f"    📱 Grupo ID: {task['group_id']}")
            print(f"    🔄 Status: {task.get('status', 'Desconhecido')}")
            print(f"    ⏰ Agendamento: {task.get('schedule', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("💡 Para ver todas as tarefas do cron:")
        print("   docker exec -it <container_name> crontab -l")
