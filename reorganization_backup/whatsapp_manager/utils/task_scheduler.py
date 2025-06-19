"""
Sistema de Agendamento de Tarefas Multiplataforma / Cross-platform Task Scheduling System

PT-BR:
Este módulo implementa um sistema de agendamento de tarefas que funciona em Windows, 
Linux e macOS. Fornece funcionalidades para criar, remover e listar tarefas agendadas,
adaptando-se automaticamente ao sistema operacional em uso.

EN:
This module implements a task scheduling system that works on Windows, Linux, and macOS.
Provides functionality to create, remove, and list scheduled tasks,
automatically adapting to the operating system in use.
"""

import os
import subprocess
import platform
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
    def get_python_executable():
        """
        PT-BR:
        Obtém o caminho absoluto do executável Python no sistema.
        
        Retorna:
            str: Caminho do executável Python
            
        Raises:
            EnvironmentError: Se não encontrar o Python

        EN:
        Gets the absolute path to Python executable in the system.
        
        Returns:
            str: Python executable path
            
        Raises:
            EnvironmentError: If Python is not found
        """
        try:
            if platform.system() == "Windows":
                python_executable = subprocess.check_output(['where', 'python'], text=True).strip().split('\n')[0]
            else:
                python_executable = subprocess.check_output(['which', 'python3'], text=True).strip()
            return os.path.abspath(python_executable)
        except Exception as e:
            raise EnvironmentError("Python não encontrado no sistema / Python not found in system") from e

    @staticmethod
    def create_task(task_name, python_script_path, schedule_type='DAILY', date=None, time='22:00'):
        """
        PT-BR:
        Cria uma tarefa agendada no sistema operacional.
        
        Parâmetros:
            task_name: Nome da tarefa
            python_script_path: Caminho do script Python
            schedule_type: Tipo de agendamento ('DAILY' ou 'ONCE')
            date: Data para execução única (formato: YYYY-MM-DD)
            time: Horário de execução (formato: HH:MM)
            
        Raises:
            NotImplementedError: Se o SO não for suportado
            Exception: Para outros erros de agendamento

        EN:
        Creates a scheduled task in the operating system.
        
        Parameters:
            task_name: Task name
            python_script_path: Python script path
            schedule_type: Schedule type ('DAILY' or 'ONCE')
            date: Date for one-time execution (format: YYYY-MM-DD)
            time: Execution time (format: HH:MM)
            
        Raises:
            NotImplementedError: If OS is not supported
            Exception: For other scheduling errors
        """
        TaskScheduled.validate_python_script(python_script_path)

        python_executable = TaskScheduled.get_python_executable()
        os_name = platform.system()

        if os_name == "Windows":
            # Corrigindo o escape de caracteres para Windows
            command = [
                'schtasks',
                '/Create',
                '/TN', task_name,
                '/TR', f'{python_executable} "{python_script_path}" --task_name {task_name}',
                '/SC', schedule_type.upper(),
                '/ST', time,
            ]
            if schedule_type.upper() == 'ONCE' and date:
                command.extend(['/SD', date])
        elif os_name == "Linux":
            # Caminho absoluto para o script que carrega o .env
            env_loader_script = "/usr/local/bin/load_env.sh"
            # Comando que será executado pelo cron
            cron_command = f"{env_loader_script} {python_executable} {python_script_path} --task_name {task_name}"
            
            if schedule_type.upper() == 'ONCE' and date:
                hour, minute = time.split(':')
                day, month, year = date.split('-') # Assuming YYYY-MM-DD format
                # Note: Cron format is MIN HOUR DAY MONTH DAY_OF_WEEK. Year is not directly supported.
                # This will run once at the specified time on the specified day/month.
                command = f'(crontab -l 2>/dev/null ; echo "{minute} {hour} {day} {month} * {cron_command} # TASK_ID:{task_name}") | crontab -'
            else: # DAILY
                hour, minute = time.split(':')
                command = f'(crontab -l 2>/dev/null ; echo "{minute} {hour} * * * {cron_command} # TASK_ID:{task_name}") | crontab -'
        elif os_name == "Darwin":  
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{safe_task_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/osascript</string>
        <string>-e</string>
        <string>tell application "Terminal" to do script "{python_executable} {python_script_path} --task_name {task_name}" </string>
    </array>"""

            if schedule_type.upper() == 'ONCE' and date:
                hour, minute = time.split(':')
                # For immediate execution (next minute), we use RunAtLoad
                current_date = datetime.now().strftime('%Y-%m-%d')
                if date == current_date:
                    plist_content += """
    <key>RunAtLoad</key>
    <true/>"""
                else:
                    plist_content += """
    <key>StartCalendarInterval</key>
    <dict>"""
                    year, month, day = date.split('-')
                    plist_content += f"""
        <key>Year</key>
        <integer>{year}</integer>
        <key>Month</key>
        <integer>{int(month)}</integer>
        <key>Day</key>
        <integer>{int(day)}</integer>
        <key>Hour</key>
        <integer>{int(hour)}</integer>
        <key>Minute</key>
        <integer>{int(minute)}</integer>
    </dict>"""
            else:
                # For daily tasks
                plist_content += """
    <key>StartCalendarInterval</key>
    <dict>"""
                hour, minute = time.split(':')
                plist_content += f"""
        <key>Hour</key>
        <integer>{int(hour)}</integer>
        <key>Minute</key>
        <integer>{int(minute)}</integer>
    </dict>"""

            plist_content += f"""
    <key>StandardOutPath</key>
    <string>/tmp/{safe_task_name}.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{safe_task_name}.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>
</dict>
</plist>
"""
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{safe_task_name}.plist")
            # Garante que o diretório ~/Library/LaunchAgents exista
            launch_dir = os.path.dirname(plist_path)
            try:
                os.makedirs(launch_dir, exist_ok=True)
            except Exception as e:
                print(f"Não foi possível criar o diretório LaunchAgents: {e}")

            uid = os.getuid()
            domain_target = f"gui/{uid}"
            # Ensure LaunchAgents directory exists
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)

            try:
                # Remove previous service if exists
                try:
                    subprocess.run(["launchctl", "stop", safe_task_name], check=False)
                    subprocess.run(["launchctl", "remove", safe_task_name], check=False)
                except:
                    pass
                try:
                    os.remove(plist_path)
                except FileNotFoundError:
                    pass

                # Write plist file
                with open(plist_path, "w") as plist_file:
                    plist_file.write(plist_content)

                # Load and start service
                subprocess.run(["launchctl", "bootstrap", domain_target, plist_path], check=True)
                subprocess.run(["launchctl", "enable", f"{domain_target}/{safe_task_name}"], check=True)
                
                print(f"Service {task_name} configured and started successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error configuring service: {str(e)}")
                try:
                    os.remove(plist_path)
                except:
                    pass
                raise Exception(f"Failed to configure service: {str(e)}")
        else:
            raise NotImplementedError("Sistema operacional não suportado para agendamento.")

        try:
            # Executa o comando construído para criar a tarefa conforme o sistema operacional
            if os_name == "Windows":
                subprocess.run(command, check=True, text=True)
            elif os_name in ["Linux", "Darwin"]:
                subprocess.run(command, shell=(os_name != "Windows"), check=True)
            print(f"Tarefa '{task_name}' criada com sucesso no sistema operacional {os_name}!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar a tarefa: {e}")
            raise

    @staticmethod
    def delete_task(task_name):
        """
        PT-BR:
        Remove uma tarefa agendada do sistema.
        
        Parâmetros:
            task_name: Nome da tarefa a ser removida
            
        Raises:
            NotImplementedError: Se o SO não for suportado
            Exception: Para erros na remoção

        EN:
        Removes a scheduled task from the system.
        
        Parameters:
            task_name: Name of task to remove
            
        Raises:
            NotImplementedError: If OS is not supported
            Exception: For removal errors
        """
        os_name = platform.system()
        if os_name == "Windows":
            command = [
                'schtasks',
                '/Delete',
                '/TN', task_name,
                '/F'
            ]
        elif os_name == "Linux":
            # Remove a tarefa do crontab filtrando pela tag # TASK_ID:{task_name}
            command = f"crontab -l 2>/dev/null | grep -v '# TASK_ID:{task_name}' | crontab -"
        elif os_name == "Darwin":  
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{safe_task_name}.plist")
            # Garante que o diretório ~/Library/LaunchAgents exista
            launch_dir = os.path.dirname(plist_path)
            try:
                os.makedirs(launch_dir, exist_ok=True)
            except Exception as e:
                print(f"Não foi possível criar o diretório LaunchAgents: {e}")

            uid = os.getuid()
            domain_target = f"gui/{uid}"
            
            try:
                # Primeiro tenta parar o serviço
                subprocess.run(["launchctl", "stop", safe_task_name], check=False)
                
                # Tenta remover o serviço do launchd
                subprocess.run(["launchctl", "unload", plist_path], check=False)
                subprocess.run(["launchctl", "remove", safe_task_name], check=False)
                
                # Remove o arquivo plist
                try:
                    if os.path.exists(plist_path):
                        os.remove(plist_path)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    subprocess.run(["sudo", "rm", plist_path], check=False)
                
                print(f"Service {task_name} stopped and removed successfully")
                return True
            except Exception as e:
                print(f"Error removing service: {str(e)}")
                try:
                    if os.path.exists(plist_path):
                        os.remove(plist_path)
                except:
                    pass
                raise Exception(f"Falha ao remover o serviço: {str(e)}")
        else:
            raise NotImplementedError("Sistema operacional não suportado para remoção de agendamento.")

        try:
            if os_name == "Windows":
                subprocess.run(command, check=True, text=True)
            elif os_name in ["Linux", "Darwin"]:
                subprocess.run(command, shell=(os_name != "Windows"), check=True)
            print(f"Tarefa '{task_name}' removida com sucesso no sistema operacional {os_name}!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao remover a tarefa: {e}")
            raise

    @staticmethod
    def list_tasks():
        """
        PT-BR:
        Lista todas as tarefas agendadas no sistema.
        
        Raises:
            NotImplementedError: Se o SO não for suportado
            Exception: Para erros na listagem

        EN:
        Lists all scheduled tasks in the system.
        
        Raises:
            NotImplementedError: If OS is not supported
            Exception: For listing errors
        """
        os_name = platform.system()

        if os_name == "Windows":
            command = [
                'schtasks',
                '/Query',
                '/FO', 'TABLE'
            ]
        elif os_name == "Linux":
            command = "crontab -l 2>/dev/null"
        elif os_name == "Darwin":  
            # Comando mais simples e eficiente para listar tarefas no macOS
            command = ["launchctl", "list"]
        else:
            raise NotImplementedError("Sistema operacional não suportado para listagem de agendamentos.")
        # Pre-initialize result to avoid unbound variable issues
        result = ''

        try:
            # Executa o comando de listagem e mostra o resultado ao usuário
            if os_name == "Windows":
                result = subprocess.check_output(command, text=True)
                print(f"Tarefas agendadas no sistema operacional {os_name}:")
                print(result)
            elif os_name == "Linux":
                result = subprocess.check_output(command, shell=True, text=True)
                print(f"Tarefas agendadas no sistema operacional {os_name}:")
                print(result)
            elif os_name == "Darwin":
                result = subprocess.check_output(command, text=True)
                print(f"Tarefas agendadas no sistema operacional {os_name}:")
                
                # Filtrar e formatar melhor as tarefas relacionadas ao projeto
                lines = result.strip().split('\n')
                project_tasks = []
                all_tasks = []
                
                for line in lines:
                    if line.strip():
                        all_tasks.append(line)
                        # Filtrar tarefas que começam com ResumoGrupo
                        if 'ResumoGrupo' in line:
                            project_tasks.append(line)
                
                if project_tasks:
                    print("=== TAREFAS DO PROJETO (WhatsApp Manager) ===")
                    for task in project_tasks:
                        print(f"  {task}")
                    print(f"\nTotal de tarefas do projeto: {len(project_tasks)}")
                else:
                    print("=== NENHUMA TAREFA DO PROJETO ENCONTRADA ===")
                
                print(f"\n=== TODAS AS TAREFAS DO SISTEMA ({len(all_tasks)} total) ===")
                for task in all_tasks[:10]:  # Mostrar apenas as primeiras 10 para não poluir
                    print(f"  {task}")
                if len(all_tasks) > 10:
                    print(f"  ... e mais {len(all_tasks) - 10} tarefas")
                    
        except subprocess.CalledProcessError as e:
            print(f"Erro ao listar as tarefas: {e}")
            raise

    @staticmethod
    def open_in_terminal(task_name, python_script_path):
        """
        PT-BR:
        Abre o script em uma nova janela do terminal.
        
        Parâmetros:
            task_name: Nome da tarefa
            python_script_path: Caminho do script Python
            
        Raises:
            Exception: Para erros ao abrir o terminal

        EN:
        Opens the script in a new terminal window.
        
        Parameters:
            task_name: Task name
            python_script_path: Python script path
            
        Raises:
            Exception: For terminal opening errors
        """
        python_executable = TaskScheduled.get_python_executable()
        command_line = f'"{python_executable}" "{python_script_path}" --task_name {task_name}'
        os_name = platform.system()

        try:
            if os_name == "Windows":
                # Abre o prompt do Windows e mantém a janela aberta
                subprocess.Popen(f'start cmd /k {command_line}', shell=True)
            elif os_name == "Linux":
                # Abre o terminal do GNOME; se usar outro, ajuste aqui
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f'{command_line}; exec bash'])
            elif os_name == "Darwin":
                # Usa AppleScript para abrir o Terminal no macOS
                subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{command_line}"'])
            if os_name == "Windows":
                # Abre o prompt do Windows e mantém a janela aberta
                subprocess.Popen(f'start cmd /k {command_line}', shell=True)
            elif os_name == "Linux":
                # Abre o terminal do GNOME; se usar outro, ajuste aqui
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f'{command_line}; exec bash'])
            elif os_name == "Darwin":
                # Usa AppleScript para abrir o Terminal no macOS
                subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{command_line}"'])
            print("Terminal aberto para exibir a execução do script.")
        except Exception as e:
            print(f"Erro ao abrir o terminal: {e}")

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
        os_name = platform.system()
        project_tasks = []
        
        if os_name == "Darwin":
            try:
                # Listar todas as tarefas
                result = subprocess.check_output(["launchctl", "list"], text=True)
                lines = result.strip().split('\n')
                
                for line in lines:
                    if 'ResumoGrupo' in line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            pid = parts[0].strip()
                            exit_code = parts[1].strip()
                            label = parts[2].strip()
                            
                            # Tentar obter mais detalhes da tarefa
                            try:
                                detail_result = subprocess.check_output(
                                    ["launchctl", "list", label], 
                                    text=True, 
                                    stderr=subprocess.DEVNULL
                                )
                                
                                # Extrair informações relevantes
                                task_info = {
                                    'label': label,
                                    'pid': pid if pid != '-' else 'Não executando',
                                    'exit_code': exit_code,
                                    'status': 'Ativo' if pid != '-' else 'Parado',
                                    'group_id': label.replace('ResumoGrupo_', '').replace('_g_us', '')
                                }
                                
                                # Tentar extrair horário de agendamento do arquivo plist
                                plist_path = f"~/Library/LaunchAgents/{label}.plist"
                                expanded_path = os.path.expanduser(plist_path)
                                if os.path.exists(expanded_path):
                                    task_info['plist_file'] = expanded_path
                                
                                project_tasks.append(task_info)
                                
                            except subprocess.CalledProcessError:
                                # Se não conseguir detalhes, adicionar informação básica
                                project_tasks.append({
                                    'label': label,
                                    'pid': pid if pid != '-' else 'Não executando',
                                    'exit_code': exit_code,
                                    'status': 'Ativo' if pid != '-' else 'Parado',
                                    'group_id': label.replace('ResumoGrupo_', '').replace('_g_us', '')
                                })
                
                return project_tasks
                
            except subprocess.CalledProcessError as e:
                print(f"Erro ao listar tarefas do projeto: {e}")
                return []
        
        elif os_name == "Linux":
            try:
                result = subprocess.check_output("crontab -l 2>/dev/null", shell=True, text=True)
                lines = result.strip().split('\n')
                
                for line in lines:
                    if 'ResumoGrupo' in line and 'TASK_ID:' in line:
                        # Extrair informações do crontab
                        parts = line.split('#')
                        if len(parts) >= 2:
                            cron_schedule = parts[0].strip()
                            task_id = parts[1].replace('TASK_ID:', '').strip()
                            
                            project_tasks.append({
                                'label': task_id,
                                'schedule': cron_schedule,
                                'type': 'cron',
                                'group_id': task_id.replace('ResumoGrupo_', '').replace('_g_us', '')
                            })
                
                return project_tasks
                
            except subprocess.CalledProcessError:
                return []
        
        elif os_name == "Windows":
            try:
                result = subprocess.check_output(['schtasks', '/Query', '/FO', 'CSV'], text=True)
                lines = result.strip().split('\n')
                
                for line in lines[1:]:  # Skip header
                    if 'ResumoGrupo' in line:
                        parts = [p.strip('"') for p in line.split('","')]
                        if len(parts) >= 2:
                            project_tasks.append({
                                'label': parts[0],
                                'status': parts[2] if len(parts) > 2 else 'Unknown',
                                'type': 'schtasks',
                                'group_id': parts[0].replace('ResumoGrupo_', '').replace('_g_us', '')
                            })
                
                return project_tasks
                
            except subprocess.CalledProcessError:
                return []
        
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
            
            if 'pid' in task:
                print(f"    🆔 PID: {task['pid']}")
            
            if 'schedule' in task:
                print(f"    ⏰ Agendamento: {task['schedule']}")
            
            if 'plist_file' in task:
                print(f"    📄 Arquivo: {task['plist_file']}")
        
        print("\n" + "=" * 60)
        print("💡 Para ver mais detalhes de uma tarefa específica:")
        print("   launchctl list <nome_da_tarefa>")
        print("💡 Para ver o arquivo de configuração:")
        print("   cat ~/Library/LaunchAgents/<nome_da_tarefa>.plist")

"""
if __name__ == "__main__":
    task_name = "MinhaTarefa"
    # Ajuste o caminho do script conforme necessário
    if platform.system() == "Windows":
        python_script = os.path.join("D:\\GOOGLE DRIVE\\Python-Projects\\crewai_2\\groups\\", "poema.py")
    else:
        python_script = os.path.join(os.path.expanduser("~"), "path", "para", "seu", "script", "poema.py")

    # Cria a tarefa agendada
    try:
        TaskScheduled.create_task(task_name, python_script, schedule_type='DAILY', time='11:13')
    except Exception as e:
        print(f"Erro ao criar a tarefa: {e}")

    # Abre uma janela do terminal para exibir a execução do script
    try:
        TaskScheduled.open_in_terminal(task_name, python_script)
    except Exception as e:
        print(f"Erro ao abrir o terminal: {e}")

    # Exemplo de remoção e listagem de tarefas
    try:
        TaskScheduled.delete_task(task_name)
    except Exception as e:
        print(f"Erro ao deletar a tarefa: {e}")

    try:
        TaskScheduled.list_tasks()
    except Exception as e:
        print(f"Erro ao listar as tarefas: {e}")
"""