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
import logging
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/app/data/docker_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DockerTaskScheduler")

class DockerTaskScheduler:
    """Task scheduling implementation for Docker environments."""
    
    @staticmethod
    def validate_python_script(python_script_path: str) -> None:
        """
        Validates if the specified Python script exists in the system.
        
        Parameters:
            python_script_path: Path to script to validate
            
        Raises:
            FileNotFoundError: If script is not found
        """
        if not os.path.exists(python_script_path):
            error_msg = f"Script Python não encontrado / Python script not found: '{python_script_path}'"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    @staticmethod
    def create_task(task_name: str, 
                   python_script_path: str, 
                   schedule_type: str = 'DAILY',
                   date: Optional[str] = None, 
                   time: str = '22:00',
                   arguments: Optional[List[str]] = None) -> bool:
        """
        Creates a scheduled task in Linux cron (Docker).
        
        Parameters:
            task_name: Task name
            python_script_path: Python script path
            schedule_type: Schedule type ('DAILY' or 'ONCE')
            date: Date for one-time execution (format: YYYY-MM-DD)
            time: Execution time (format: HH:MM)
            arguments: Optional list of arguments to pass to the script
            
        Returns:
            bool: True if task was created successfully
            
        Raises:
            Exception: For scheduling errors
        """
        logger.info(f"Creating Docker task: {task_name}, script: {python_script_path}, "
                   f"schedule: {schedule_type}, time: {time}")
        
        DockerTaskScheduler.validate_python_script(python_script_path)

        # In Docker, always use python3
        python_executable = "python3"
        
        # Generate arguments string if provided
        args_str = ""
        if arguments:
            args_str = " ".join([str(arg) for arg in arguments])
        
        # Command to be executed by cron (use load_env.sh script)
        env_loader_script = "/usr/local/bin/load_env.sh"
        cron_command = f"{env_loader_script} {python_executable} {python_script_path} --task_name {task_name}"
        
        if args_str:
            cron_command += f" {args_str}"
        
        if schedule_type.upper() == 'ONCE' and date:
            # For 'ONCE' execution, convert to daily with date check in the script
            hour, minute = time.split(':')
            logger.info(f"Converting ONCE to DAILY with date check for {date}")
        else:  # DAILY
            hour, minute = time.split(':')
        
        # Create a file directly in /etc/cron.d/ with proper permissions
        safe_name = task_name.replace('@', '_').replace('.', '_')
        cron_file_path = f"/etc/cron.d/task_{safe_name}"
        
        try:
            # Create cron file with proper content
            cron_content = f"# Task created on {datetime.now()}\n"
            cron_content += "SHELL=/bin/bash\n"
            cron_content += "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
            cron_content += "PYTHONPATH=/app:/app/src:/app/src_clean\n\n"
            cron_content += f"{minute} {hour} * * * root {cron_command} >> /app/data/task_{safe_name}.log 2>&1 # TASK_ID:{task_name}\n"
            
            # Write to file
            with open(cron_file_path, 'w') as cron_file:
                cron_file.write(cron_content)
            
            # Set permissions
            subprocess.run(['chmod', '0644', cron_file_path], check=True)
            subprocess.run(['chown', 'root:root', cron_file_path], check=True)
            
            # Check if cron is running, if not, start it
            try:
                subprocess.run("service cron status || service cron start", shell=True, check=True)
            except Exception as e:
                logger.warning(f"Could not check/start cron service: {e}")
            
            logger.info(f"Task '{task_name}' created successfully in Docker's cron!")
            return True
            
        except Exception as e:
            logger.error(f"Error creating task '{task_name}': {e}")
            raise RuntimeError(f"Failed to create Docker task: {str(e)}")

    @staticmethod
    def delete_task(task_name: str) -> bool:
        """
        Removes a scheduled task from cron.
        
        Parameters:
            task_name: Name of task to remove
            
        Returns:
            bool: True if task was removed successfully
            
        Raises:
            Exception: For removal errors
        """
        logger.info(f"Removing Docker task: {task_name}")
        
        # Name of file to remove
        safe_name = task_name.replace('@', '_').replace('.', '_')
        cron_file_path = f"/etc/cron.d/task_{safe_name}"
        
        try:
            # Check if file exists and remove it
            if os.path.exists(cron_file_path):
                os.remove(cron_file_path)
                logger.info(f"Task '{task_name}' removed successfully from cron!")
                return True
            else:
                # If file not found, try removing from crontab as well (for compatibility)
                command = f"crontab -l 2>/dev/null | grep -v '# TASK_ID:{task_name}' | crontab -"
                subprocess.run(command, shell=True, check=True, text=True)
                logger.info(f"Task '{task_name}' removed successfully from crontab!")
                return True
        except Exception as e:
            logger.error(f"Error removing task '{task_name}': {e}")
            raise RuntimeError(f"Failed to remove Docker task: {str(e)}")

    @staticmethod
    def list_tasks() -> List[Dict[str, str]]:
        """
        Lists all scheduled tasks in cron.
        
        Returns:
            List of task information dictionaries
        """
        tasks = []
        logger.info("Listing all Docker tasks")
        
        # Check files in /etc/cron.d/ related to the project
        try:
            # List files in /etc/cron.d/ that start with "task_"
            cron_d_files = []
            try:
                cron_d_files = [f for f in os.listdir('/etc/cron.d/') if f.startswith('task_')]
            except Exception as e:
                logger.warning(f"Could not list files in /etc/cron.d/: {e}")
            
            for file in cron_d_files:
                try:
                    with open(f"/etc/cron.d/{file}", 'r') as f:
                        content = f.read()
                        task_id = None
                        
                        # Extract important information
                        for line in content.split('\n'):
                            if '# TASK_ID:' in line:
                                task_id_parts = line.split('# TASK_ID:')
                                if len(task_id_parts) == 2:
                                    task_id = task_id_parts[1].strip()
                                    break
                        
                        if task_id:
                            # Extract schedule information
                            schedule_info = "Unknown"
                            for line in content.split('\n'):
                                if line and not line.startswith('#') and any(c.isdigit() for c in line):
                                    parts = line.strip().split()
                                    if len(parts) >= 2:
                                        schedule_info = f"{parts[0]} {parts[1]} * * *"
                                        break
                            
                            tasks.append({
                                'name': task_id,
                                'schedule': schedule_info,
                                'status': 'Active',
                                'file': f'/etc/cron.d/{file}'
                            })
                except Exception as e:
                    logger.warning(f"Error processing file {file}: {e}")
        
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
        
        # Also check user's crontab (for compatibility)
        try:
            result = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '# TASK_ID:' in line:
                        parts = line.split('# TASK_ID:')
                        if len(parts) == 2:
                            task_name = parts[1].strip()
                            cron_schedule = parts[0].strip()
                            
                            # Check if this task already exists in the list
                            if not any(task['name'] == task_name for task in tasks):
                                tasks.append({
                                    'name': task_name,
                                    'schedule': cron_schedule,
                                    'status': 'Active',
                                    'file': 'crontab'
                                })
        except Exception as e:
            logger.warning(f"Error checking crontab: {e}")
        
        logger.info(f"Found {len(tasks)} tasks in Docker")
        return tasks

    @staticmethod
    def list_project_tasks() -> List[Dict[str, str]]:
        """
        Lists only tasks related to the project.
        
        Returns:
            List of project tasks with details
        """
        tasks = DockerTaskScheduler.list_tasks()
        
        # Filter for project-related tasks
        project_tasks = [task for task in tasks 
                        if task['name'].startswith('GroupSummary_') or
                           task['name'].startswith('ResumoGrupo_')]
        
        logger.info(f"Found {len(project_tasks)} project tasks in Docker")
        return project_tasks
