#!/usr/bin/env python3
"""
Docker Task Scheduler Test Tool

This script tests task scheduling in Docker environments by creating, listing
and deleting test tasks.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Ensure the src_clean directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from src_clean.whatsapp_manager.infrastructure.scheduling.task_scheduler import TaskSchedulingService
    from src_clean.whatsapp_manager.infrastructure.scheduling.docker_task_scheduler import DockerTaskScheduler
except ImportError:
    print("Error: Could not import scheduling classes. Make sure you're running this from the project root.")
    sys.exit(1)

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def is_docker():
    """Check if running in Docker."""
    docker_indicators = ['/.dockerenv', '/proc/1/cgroup']
    for indicator in docker_indicators:
        if os.path.exists(indicator):
            return True
    
    # Check typical Docker directory structure
    if os.path.exists('/app') and os.path.exists('/app/data'):
        return True
        
    return False

def create_test_script():
    """Create a test Python script for scheduling."""
    script_dir = os.path.join(project_root, "tools", "test_scripts")
    os.makedirs(script_dir, exist_ok=True)
    
    script_path = os.path.join(script_dir, "docker_scheduled_test.py")
    
    with open(script_path, "w") as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Create log directory if it doesn't exist
log_dir = "/app/data" if os.path.exists("/app/data") else "/tmp"

# Write to log file
with open(os.path.join(log_dir, "scheduled_task_test.log"), "a") as log:
    log.write(f"[{datetime.now()}] Test scheduled task executed\\n")
    
    # Add command line arguments to log
    if len(sys.argv) > 1:
        log.write(f"[{datetime.now()}] Arguments: {sys.argv[1:]}\\n")
    
    # Add some system info
    log.write(f"[{datetime.now()}] Python version: {sys.version}\\n")
    log.write(f"[{datetime.now()}] Current directory: {os.getcwd()}\\n")
    log.write(f"[{datetime.now()}] Environment variables: PATH={os.environ.get('PATH', 'Not set')}\\n")
    log.write(f"[{datetime.now()}] Task completed successfully\\n\\n")
""")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    return script_path

def test_scheduling():
    """Test the scheduling functionality."""
    print_section("DOCKER TASK SCHEDULER TEST")
    
    # Check if running in Docker
    if not is_docker():
        print("⚠️ This script should ideally run in Docker for full testing")
        print("Continuing test assuming Docker compatibility...")
    else:
        print("✅ Running in Docker environment")
    
    # Create test script
    print("\nCreating test script...")
    script_path = create_test_script()
    print(f"✅ Test script created: {script_path}")
    
    # Initialize TaskSchedulingService
    print("\nInitializing TaskSchedulingService...")
    scheduler = TaskSchedulingService()
    print(f"✅ Scheduler initialized, Docker mode: {scheduler.is_docker}")
    
    # Test task name
    task_name = f"TestTask_{int(time.time())}"
    
    try:
        # Create a daily task
        print(f"\nCreating daily task: {task_name}_daily...")
        daily_result = scheduler.create_task(
            task_name=f"{task_name}_daily",
            python_script_path=script_path,
            schedule_type="DAILY",
            time=(datetime.now() + timedelta(minutes=1)).strftime("%H:%M"),
            arguments=["daily_test"]
        )
        print(f"✅ Daily task created: {daily_result}")
        
        # Create a one-time task
        print(f"\nCreating one-time task: {task_name}_once...")
        once_result = scheduler.create_task(
            task_name=f"{task_name}_once",
            python_script_path=script_path,
            schedule_type="ONCE",
            date=datetime.now().strftime("%Y-%m-%d"),
            time=(datetime.now() + timedelta(minutes=2)).strftime("%H:%M"),
            arguments=["once_test"]
        )
        print(f"✅ Once task created: {once_result}")
        
        # List all tasks
        print("\nListing all tasks...")
        tasks = scheduler.list_tasks()
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"- {task}")
            
        # Pause to allow checking
        print("\nWaiting 5 seconds for tasks to be visible in system...")
        time.sleep(5)
        
        # Delete tasks
        print(f"\nDeleting daily task: {task_name}_daily...")
        delete_daily = scheduler.delete_task(f"{task_name}_daily")
        print(f"✅ Daily task deleted: {delete_daily}")
        
        print(f"\nDeleting one-time task: {task_name}_once...")
        delete_once = scheduler.delete_task(f"{task_name}_once")
        print(f"✅ Once task deleted: {delete_once}")
        
        # List all tasks again to confirm deletion
        print("\nListing all tasks after deletion...")
        tasks = scheduler.list_tasks()
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"- {task}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    print_section("TEST SUMMARY")
    print("Test completed. Check for any error messages above.")
    print("\nTo verify task execution (if you didn't delete tasks immediately):")
    print("- Check /app/data/scheduled_task_test.log or /tmp/scheduled_task_test.log")
    print("- Check /app/data/task_*.log files for task output")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_scheduling())
