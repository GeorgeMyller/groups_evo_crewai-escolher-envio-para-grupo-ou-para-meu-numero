"""
Sistema de Agendamento de Tarefas Multiplataforma / Cross-platform Task Scheduling System

PT-BR:
Este módulo implementa um sistema de agendamento de tarefas que funciona em Windows, 
Linux, macOS e Docker. Fornece funcionalidades para criar, remover e listar tarefas agendadas,
adaptando-se automaticamente ao sistema operacional ou ambiente em uso.

EN:
This module implements a task scheduling system that works on Windows, Linux, macOS, and Docker.
Provides functionality to create, remove, and list scheduled tasks,
automatically adapting to the operating system or environment in use.
"""

import os
import subprocess
import platform
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum

from enum import Enum

def is_running_in_docker() -> bool:
    """
    Detects if the code is running inside a Docker container.
    
    Returns:
        bool: True if running in Docker, False otherwise
    """
    # Check Docker environment variable (most reliable)
    docker_env = os.environ.get('DOCKER_ENV', '').lower() == 'true'
    if docker_env:
        return True
    
    # Check for Docker-specific files
    docker_indicators = [
        '/.dockerenv',
        '/proc/1/cgroup'
    ]
    
    for indicator in docker_indicators:
        if os.path.exists(indicator):
            if indicator == '/proc/1/cgroup':
                try:
                    with open(indicator, 'r') as f:
                        content = f.read()
                        if 'docker' in content or 'containerd' in content:
                            return True
                except:
                    pass
            else:
                return True
    
    # Check hostname
    try:
        with open('/etc/hostname', 'r') as f:
            hostname = f.read().strip()
            if hostname.startswith('container') or hostname.startswith('docker'):
                return True
    except:
        pass
    
    # Check for Docker marker file
    if os.path.exists('/app/.docker_environment'):
        return True
    
    # Check for typical Docker directory structure
    if os.path.exists('/app') and os.path.exists('/app/src') and os.path.exists('/app/data'):
        return True
    
    # Check for supervisord running (typical in our Docker setup)
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if 'supervisord' in result.stdout:
            return True
    except:
        pass
    
    return False


class ScheduleType(Enum):
    """Schedule type enumeration."""
    DAILY = "DAILY"
    ONCE = "ONCE"


class OperatingSystem(Enum):
    """Supported operating systems."""
    WINDOWS = "Windows"
    LINUX = "Linux"
    DARWIN = "Darwin"  # macOS


class TaskSchedulingService:
    """
    Cross-platform task scheduling service with Docker support.
    """
    
    def __init__(self):
        """Initialize the task scheduling service."""
        self.is_docker = is_running_in_docker()
        self.os_name = platform.system()
        self._validate_os_support()
        
        if self.is_docker:
            # Import Docker scheduler dynamically to avoid import issues
            from .docker_task_scheduler import DockerTaskScheduler
            self.docker_scheduler = DockerTaskScheduler
    
    def _validate_os_support(self) -> None:
        """Validate that the current OS is supported."""
        if self.is_docker:
            # Docker is always supported
            return
            
        supported_systems = [os.value for os in OperatingSystem]
        if self.os_name not in supported_systems:
            raise NotImplementedError(f"Operating system '{self.os_name}' is not supported")
    
    def validate_python_script(self, python_script_path: str) -> None:
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
            raise FileNotFoundError(
                f"Script Python não encontrado / Python script not found: '{python_script_path}'"
            )
    
    def get_python_executable(self) -> str:
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
            if self.os_name == OperatingSystem.WINDOWS.value:
                result = subprocess.check_output(['where', 'python'], text=True)
                python_executable = result.strip().split('\n')[0]
            else:
                result = subprocess.check_output(['which', 'python3'], text=True)
                python_executable = result.strip()
            
            return os.path.abspath(python_executable)
            
        except Exception as e:
            raise EnvironmentError("Python não encontrado no sistema / Python not found in system") from e
    
    def create_task(self, 
                   task_name: str, 
                   python_script_path: str, 
                   schedule_type: Union[str, ScheduleType] = ScheduleType.DAILY,
                   date: Optional[str] = None, 
                   time: str = '22:00',
                   arguments: Optional[List[str]] = None) -> bool:
        """
        PT-BR:
        Cria uma tarefa agendada no sistema operacional ou no Docker.
        
        Parâmetros:
            task_name: Nome da tarefa
            python_script_path: Caminho do script Python
            schedule_type: Tipo de agendamento ('DAILY' ou 'ONCE')
            date: Data para execução única (formato: YYYY-MM-DD)
            time: Horário de execução (formato: HH:MM)
            arguments: Argumentos opcionais para passar ao script
            
        Returns:
            bool: True se a tarefa foi criada com sucesso
            
        Raises:
            Exception: Para erros de agendamento

        EN:
        Creates a scheduled task in the operating system or Docker.
        
        Parameters:
            task_name: Task name
            python_script_path: Python script path
            schedule_type: Schedule type ('DAILY' or 'ONCE')
            date: Date for one-time execution (format: YYYY-MM-DD)
            time: Execution time (format: HH:MM)
            arguments: Optional arguments to pass to the script
            
        Returns:
            bool: True if task was created successfully
            
        Raises:
            Exception: For scheduling errors
        """
        # Check if running in Docker and use Docker scheduler if so
        if self.is_docker:
            return self.docker_scheduler.create_task(
                task_name=task_name,
                python_script_path=python_script_path,
                schedule_type=schedule_type.value if isinstance(schedule_type, ScheduleType) else schedule_type,
                date=date,
                time=time,
                arguments=arguments
            )
        
        # Continue with standard OS schedulers
        # Validate inputs
        self.validate_python_script(python_script_path)
        
        # Convert schedule_type to enum if string
        if isinstance(schedule_type, str):
            schedule_type = ScheduleType(schedule_type.upper())
        
        python_executable = self.get_python_executable()
        
        try:
            if self.os_name == OperatingSystem.WINDOWS.value:
                return self._create_windows_task(task_name, python_executable, python_script_path, 
                                                schedule_type, date, time)
            elif self.os_name == OperatingSystem.LINUX.value:
                return self._create_linux_task(task_name, python_executable, python_script_path, 
                                              schedule_type, date, time)
            elif self.os_name == OperatingSystem.DARWIN.value:
                return self._create_macos_task(task_name, python_executable, python_script_path, 
                                              schedule_type, date, time)
            else:
                return False
        except Exception as e:
            raise RuntimeError(f"Failed to create task '{task_name}': {str(e)}") from e
    
    def _create_windows_task(self, task_name: str, python_executable: str, 
                           python_script_path: str, schedule_type: ScheduleType,
                           date: Optional[str], time: str) -> bool:
        """Create a Windows scheduled task."""
        command = [
            'schtasks',
            '/Create',
            '/TN', task_name,
            '/TR', f'{python_executable} "{python_script_path}" --task_name {task_name}',
            '/SC', schedule_type.value,
            '/ST', time,
        ]
        
        if schedule_type == ScheduleType.ONCE and date:
            command.extend(['/SD', date])
        
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0
    
    def _create_linux_task(self, task_name: str, python_executable: str, 
                          python_script_path: str, schedule_type: ScheduleType,
                          date: Optional[str], time: str) -> bool:
        """Create a Linux cron task."""
        # Environment loader script path
        env_loader_script = "/usr/local/bin/load_env.sh"
        cron_command = f"{env_loader_script} {python_executable} {python_script_path} --task_name {task_name}"
        
        if schedule_type == ScheduleType.ONCE and date:
            hour, minute = time.split(':')
            day, month, year = date.split('-')  # YYYY-MM-DD format
            cron_entry = f"{minute} {hour} {day} {month} * {cron_command} # TASK_ID:{task_name}"
        else:  # DAILY
            hour, minute = time.split(':')
            cron_entry = f"{minute} {hour} * * * {cron_command} # TASK_ID:{task_name}"
        
        command = f'(crontab -l 2>/dev/null ; echo "{cron_entry}") | crontab -'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    def _create_macos_task(self, task_name: str, python_executable: str, 
                          python_script_path: str, schedule_type: ScheduleType,
                          date: Optional[str], time: str) -> bool:
        """Create a macOS launchd task."""
        safe_task_name = task_name.replace('@', '_').replace('.', '_')
        plist_content = self._generate_macos_plist(
            safe_task_name, python_executable, python_script_path, task_name,
            schedule_type, date, time
        )
        
        # Write plist file
        plist_path = f"/tmp/{safe_task_name}.plist"
        try:
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load the plist
            result = subprocess.run(['launchctl', 'load', plist_path], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(plist_path):
                os.remove(plist_path)
    
    def _generate_macos_plist(self, safe_task_name: str, python_executable: str,
                             python_script_path: str, task_name: str,
                             schedule_type: ScheduleType, date: Optional[str], 
                             time: str) -> str:
        """Generate macOS plist content for scheduled task."""
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
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
    </array>'''

        if schedule_type == ScheduleType.ONCE and date:
            hour, minute = time.split(':')
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            if date == current_date:
                plist_content += '''
    <key>RunAtLoad</key>
    <true/>'''
            else:
                year, month, day = date.split('-')
                plist_content += f'''
    <key>StartCalendarInterval</key>
    <dict>
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
    </dict>'''
        else:
            # Daily tasks
            hour, minute = time.split(':')
            plist_content += f'''
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{int(hour)}</integer>
        <key>Minute</key>
        <integer>{int(minute)}</integer>
    </dict>'''

        plist_content += f'''
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
</plist>'''
        
        return plist_content
    
    def remove_task(self, task_name: str) -> bool:
        """
        Remove a scheduled task.
        
        Parameters:
            task_name: Name of the task to remove
            
        Returns:
            bool: True if task was removed successfully
        """
        # Use Docker scheduler if in Docker
        if self.is_docker:
            return self.docker_scheduler.delete_task(task_name)
            
        # Otherwise use standard OS schedulers
        try:
            if self.os_name == OperatingSystem.WINDOWS.value:
                result = subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
                
            elif self.os_name == OperatingSystem.LINUX.value:
                # Remove from crontab
                command = f'crontab -l 2>/dev/null | grep -v "TASK_ID:{task_name}" | crontab -'
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0
                
            elif self.os_name == OperatingSystem.DARWIN.value:
                safe_task_name = task_name.replace('@', '_').replace('.', '_')
                result = subprocess.run(['launchctl', 'unload', f"/tmp/{safe_task_name}.plist"], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            else:
                return False
                
        except Exception:
            return False
            
    def delete_task(self, task_name: str) -> bool:
        """
        Alias for remove_task to maintain API compatibility.
        
        Parameters:
            task_name: Name of the task to delete
            
        Returns:
            bool: True if task was deleted successfully
        """
        return self.remove_task(task_name)
    
    def list_tasks(self) -> List[Dict[str, str]]:
        """
        List all scheduled tasks.
        
        Returns:
            List of task information dictionaries
        """
        # Use Docker scheduler if in Docker
        if self.is_docker:
            return self.docker_scheduler.list_tasks()
            
        # Otherwise use standard OS schedulers
        tasks = []
        
        try:
            if self.os_name == OperatingSystem.WINDOWS.value:
                result = subprocess.run(['schtasks', '/Query', '/FO', 'CSV'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse CSV output (simplified)
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            tasks.append({
                                'name': parts[0].strip('"'),
                                'status': parts[1].strip('"'),
                                'platform': 'Windows'
                            })
                            
            elif self.os_name == OperatingSystem.LINUX.value:
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'TASK_ID:' in line:
                            task_id = line.split('TASK_ID:')[1].strip()
                            tasks.append({
                                'name': task_id,
                                'status': 'Active',
                                'platform': 'Linux'
                            })
                            
            elif self.os_name == OperatingSystem.DARWIN.value:
                result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                        parts = line.split()
                        if len(parts) >= 3:
                            tasks.append({
                                'name': parts[2],
                                'status': 'Active' if parts[0] != '-' else 'Inactive',
                                'platform': 'macOS'
                            })
                            
        except Exception:
            pass  # Return empty list on error
        
        return tasks
