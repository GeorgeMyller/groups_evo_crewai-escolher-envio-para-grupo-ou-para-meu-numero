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
        
        # Log the scheduling attempt
        log_path = "/app/data/cron_scheduling.log"
        with open(log_path, "a") as log_file:
            log_file.write(f"[{datetime.now()}] Scheduling task: {task_name}\n")
        
        # Comando que será executado pelo cron (usa o script load_env.sh)
        env_loader_script = "/usr/local/bin/load_env.sh"
        cron_command = f"{env_loader_script} {python_executable} {python_script_path} --task_name {task_name}"
        
        if schedule_type.upper() == 'ONCE' and date:
            # IMPORTANTE: Para execução "uma vez", convertemos para agendamento diário
            # pois o cron padrão não suporta anos específicos
            # O script summary.py deve verificar se já executou hoje
            hour, minute = time.split(':')
            print(f"AVISO: Agendamento 'ONCE' convertido para DAILY. Script deve verificar execução única.")
        else:  # DAILY
            hour, minute = time.split(':')
        
        # Criamos um arquivo direto em /etc/cron.d/ com permissões adequadas
        cron_file_path = f"/etc/cron.d/task_{task_name.replace('@', '_').replace('.', '_')}"
        
        try:
            # Criar o arquivo cron com o conteúdo correto
            cron_content = f"# Task created on {datetime.now()}\n"
            cron_content += "SHELL=/bin/bash\n"
            cron_content += "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
            cron_content += "PYTHONPATH=/app:/app/src\n\n"
            cron_content += f"{minute} {hour} * * * root {cron_command} >> /app/data/task_{task_name.replace('@', '_').replace('.', '_')}.log 2>&1 # TASK_ID:{task_name}\n"
            
            # Escrever para o arquivo
            with open(cron_file_path, 'w') as cron_file:
                cron_file.write(cron_content)
            
            # Definir permissões
            subprocess.run(['chmod', '0644', cron_file_path], check=True)
            subprocess.run(['chown', 'root:root', cron_file_path], check=True)
            
            # Verificar se o cron está rodando, se não, iniciar
            try:
                subprocess.run("service cron status || service cron start", shell=True, check=True)
            except:
                print("Aviso: Não foi possível verificar/iniciar o serviço cron")
            
            # Registrar sucesso no log
            with open(log_path, "a") as log_file:
                log_file.write(f"[{datetime.now()}] Task {task_name} created successfully in {cron_file_path}\n")
                
            print(f"Tarefa '{task_name}' criada com sucesso no cron do Docker!")
            return True
            
        except Exception as e:
            # Registrar erro no log
            with open(log_path, "a") as log_file:
                log_file.write(f"[{datetime.now()}] ERROR creating task {task_name}: {str(e)}\n")
                
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
        # Log the deletion attempt
        log_path = "/app/data/cron_scheduling.log"
        with open(log_path, "a") as log_file:
            log_file.write(f"[{datetime.now()}] Removing task: {task_name}\n")
        
        # Nome do arquivo para remoção
        cron_file_path = f"/etc/cron.d/task_{task_name.replace('@', '_').replace('.', '_')}"
        
        try:
            # Verifica se o arquivo existe e remove
            if os.path.exists(cron_file_path):
                os.remove(cron_file_path)
                print(f"Tarefa '{task_name}' removida com sucesso do cron!")
                
                # Registrar sucesso no log
                with open(log_path, "a") as log_file:
                    log_file.write(f"[{datetime.now()}] Task {task_name} removed successfully\n")
                    
                return True
            else:
                # Se não encontrar o arquivo, tenta remover de crontab também (compatibilidade)
                command = f"crontab -l 2>/dev/null | grep -v '# TASK_ID:{task_name}' | crontab -"
                subprocess.run(command, shell=True, check=True, text=True)
                print(f"Tarefa '{task_name}' removida com sucesso do crontab!")
                
                # Registrar sucesso no log
                with open(log_path, "a") as log_file:
                    log_file.write(f"[{datetime.now()}] Task {task_name} removed from crontab\n")
                    
                return True
        except Exception as e:
            # Registrar erro no log
            with open(log_path, "a") as log_file:
                log_file.write(f"[{datetime.now()}] ERROR removing task {task_name}: {str(e)}\n")
                
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
        try:
            print("📋 TAREFAS AGENDADAS NO CRON:")
            print("=" * 50)
            
            # Verificar o crontab do usuário primeiro
            crontab_command = "crontab -l 2>/dev/null"
            crontab_result = subprocess.run(crontab_command, shell=True, capture_output=True, text=True)
            
            if crontab_result.returncode == 0 and crontab_result.stdout.strip():
                print("Tarefas do crontab do usuário:")
                print(crontab_result.stdout)
            
            # Verificar os arquivos em /etc/cron.d/ relacionados ao projeto
            print("\nTarefas do /etc/cron.d/:")
            
            tasks_found = False
            try:
                # Listar arquivos em /etc/cron.d/ que começam com "task_"
                cron_d_files = [f for f in os.listdir('/etc/cron.d/') if f.startswith('task_')]
                
                if cron_d_files:
                    tasks_found = True
                    for file in cron_d_files:
                        print(f"\n--- Tarefa: {file} ---")
                        try:
                            with open(f"/etc/cron.d/{file}", 'r') as f:
                                content = f.read()
                                print(content)
                        except Exception as e:
                            print(f"Erro ao ler arquivo {file}: {str(e)}")
            except Exception as e:
                print(f"Erro ao listar arquivos em /etc/cron.d/: {str(e)}")
            
            # Verificar status do serviço cron
            print("\nStatus do serviço cron:")
            try:
                status_result = subprocess.run("service cron status", shell=True, capture_output=True, text=True)
                print(status_result.stdout)
                if status_result.returncode != 0:
                    print("AVISO: O serviço cron parece estar parado!")
                    print("Tentando iniciar o serviço cron...")
                    start_result = subprocess.run("service cron start", shell=True, capture_output=True, text=True)
                    if start_result.returncode == 0:
                        print("Serviço cron iniciado com sucesso!")
                    else:
                        print("ERRO: Não foi possível iniciar o serviço cron!")
            except Exception as e:
                print(f"Erro ao verificar status do cron: {str(e)}")
            
            # Se nenhuma tarefa foi encontrada
            if not tasks_found and (crontab_result.returncode != 0 or not crontab_result.stdout.strip()):
                print("\nNenhuma tarefa agendada encontrada no sistema.")
                
        except Exception as e:
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
        
        # Verificar os arquivos em /etc/cron.d/ relacionados ao projeto
        try:
            # Listar arquivos em /etc/cron.d/ que começam com "task_"
            cron_d_files = []
            try:
                cron_d_files = [f for f in os.listdir('/etc/cron.d/') if f.startswith('task_')]
            except Exception as e:
                print(f"Aviso: Não foi possível listar arquivos em /etc/cron.d/: {str(e)}")
            
            for file in cron_d_files:
                if 'ResumoGrupo' in file:
                    try:
                        with open(f"/etc/cron.d/{file}", 'r') as f:
                            content = f.read()
                            # Extrair informações importantes
                            task_id_match = None
                            for line in content.split('\n'):
                                if '# TASK_ID:' in line:
                                    task_id_parts = line.split('# TASK_ID:')
                                    if len(task_id_parts) == 2:
                                        task_id_match = task_id_parts[1].strip()
                                        break
                            
                            if task_id_match:
                                # Extrair grupo ID
                                group_id = task_id_match.split('_')[1] if '_' in task_id_match else 'Unknown'
                                
                                # Extrair agendamento (minutos e horas)
                                schedule_info = "Desconhecido"
                                for line in content.split('\n'):
                                    # Busca por linha que contém dígitos no início (padrão cron)
                                    if line and not line.startswith('#') and line[0].isdigit():
                                        parts = line.strip().split()
                                        if len(parts) >= 2:  # minuto hora ...
                                            schedule_info = f"{parts[0]} {parts[1]} * * *"  # min hora * * *
                                            break
                                
                                project_tasks.append({
                                    'label': task_id_match,
                                    'group_id': group_id,
                                    'schedule': schedule_info,
                                    'status': 'Agendado',
                                    'source': f'/etc/cron.d/{file}'
                                })
                    except Exception as e:
                        print(f"Aviso: Erro ao processar arquivo {file}: {str(e)}")
        except Exception as e:
            print(f"Aviso: Erro ao listar tarefas do projeto de /etc/cron.d/: {str(e)}")
        
        # Verificar também o crontab do usuário (compatibilidade)
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
                            
                            # Verificar se esta tarefa já existe na lista (para não duplicar)
                            if not any(task['label'] == task_name for task in project_tasks):
                                project_tasks.append({
                                    'label': task_name,
                                    'group_id': group_id,
                                    'schedule': cron_schedule,
                                    'status': 'Agendado',
                                    'source': 'crontab'
                                })
        except Exception:
            pass  # Sem tarefas agendadas no crontab
        
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
