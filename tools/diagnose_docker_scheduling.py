#!/usr/bin/env python3
"""
Docker Task Scheduler Diagnostic Tool

This script diagnoses issues with task scheduling in Docker environments
and reports the current state of scheduled tasks.
"""

import os
import sys
import subprocess
import platform
from datetime import datetime

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

def check_cron_service():
    """Check if cron service is running."""
    print_section("CRON SERVICE STATUS")
    
    try:
        # Check if cron is installed
        which_cron = subprocess.run(["which", "cron"], 
                                   capture_output=True, text=True)
        if which_cron.returncode != 0:
            print("❌ cron is not installed")
            return False
            
        print(f"✅ cron is installed: {which_cron.stdout.strip()}")
        
        # Check service status
        status = subprocess.run(["service", "cron", "status"], 
                               capture_output=True, text=True)
        
        if "running" in status.stdout.lower():
            print("✅ cron service is running")
            print(status.stdout)
            return True
        else:
            print("❌ cron service is not running")
            print(status.stdout)
            
            # Try to start cron
            print("\nAttempting to start cron service...")
            start = subprocess.run(["service", "cron", "start"], 
                                  capture_output=True, text=True)
            
            # Check again
            status = subprocess.run(["service", "cron", "status"], 
                                   capture_output=True, text=True)
            
            if "running" in status.stdout.lower():
                print("✅ cron service started successfully")
                return True
            else:
                print("❌ failed to start cron service")
                return False
                
    except Exception as e:
        print(f"❌ Error checking cron service: {e}")
        return False

def check_cron_files():
    """Check cron files in /etc/cron.d/."""
    print_section("CRON FILES (/etc/cron.d/)")
    
    try:
        # List files in /etc/cron.d/
        files = os.listdir('/etc/cron.d/')
        
        task_files = [f for f in files if f.startswith('task_')]
        other_files = [f for f in files if not f.startswith('task_')]
        
        print(f"Found {len(task_files)} task files and {len(other_files)} other files")
        
        if task_files:
            print("\nTASK FILES:")
            for file in task_files:
                print(f"\n--- {file} ---")
                try:
                    with open(f"/etc/cron.d/{file}", 'r') as f:
                        content = f.read()
                        print(content)
                except Exception as e:
                    print(f"Error reading file: {e}")
        else:
            print("\n❌ No task files found in /etc/cron.d/")
            
        print("\nOTHER CRON FILES:")
        for file in other_files[:5]:  # Show only first 5 to avoid clutter
            print(f"- {file}")
        
        if len(other_files) > 5:
            print(f"... and {len(other_files) - 5} more files")
            
    except Exception as e:
        print(f"❌ Error checking cron files: {e}")

def check_user_crontab():
    """Check user crontab."""
    print_section("USER CRONTAB")
    
    try:
        result = subprocess.run("crontab -l", shell=True, 
                               capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print("User crontab content:")
            print(result.stdout)
            
            # Check for task entries
            task_lines = [line for line in result.stdout.splitlines() 
                         if 'TASK_ID:' in line]
            
            if task_lines:
                print(f"\nFound {len(task_lines)} task entries in user crontab")
            else:
                print("\nNo task entries found in user crontab")
        else:
            print("No user crontab found or it's empty")
            
    except Exception as e:
        print(f"❌ Error checking user crontab: {e}")

def check_log_files():
    """Check relevant log files."""
    print_section("LOG FILES")
    
    log_files = [
        "/app/data/cron_scheduling.log",
        "/app/data/cron_monitor.log",
        "/app/data/cron.log",
        "/app/data/docker_scheduler.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n--- {log_file} ---")
            try:
                # Get last 10 lines
                result = subprocess.run(["tail", "-10", log_file], 
                                       capture_output=True, text=True)
                print(result.stdout)
            except Exception as e:
                print(f"Error reading log file: {e}")
        else:
            print(f"\n❌ Log file not found: {log_file}")

def check_permissions():
    """Check permissions of relevant files."""
    print_section("FILE PERMISSIONS")
    
    # Check /etc/cron.d/ permissions
    try:
        result = subprocess.run(["ls", "-la", "/etc/cron.d/"], 
                               capture_output=True, text=True)
        print("Permissions for /etc/cron.d/:")
        print(result.stdout)
    except Exception as e:
        print(f"Error checking /etc/cron.d/ permissions: {e}")
        
    # Check script permissions
    script_dirs = [
        "/app/src/whatsapp_manager/core",
        "/app/src_clean/whatsapp_manager/core"
    ]
    
    for script_dir in script_dirs:
        if os.path.exists(script_dir):
            print(f"\nPermissions for {script_dir}:")
            try:
                result = subprocess.run(["ls", "-la", script_dir], 
                                       capture_output=True, text=True)
                print(result.stdout)
            except Exception as e:
                print(f"Error checking {script_dir} permissions: {e}")

def main():
    """Main function."""
    print_section("DOCKER TASK SCHEDULER DIAGNOSTIC")
    print(f"Date and Time: {datetime.now()}")
    print(f"Platform: {platform.platform()}")
    
    # Check if running in Docker
    if not is_docker():
        print("\n❌ This script should be run inside a Docker container!")
        print("Current environment does not appear to be Docker.")
        return 1
        
    print("✅ Running in Docker environment")
    
    # Check cron service
    cron_running = check_cron_service()
    
    # Check cron files
    check_cron_files()
    
    # Check user crontab
    check_user_crontab()
    
    # Check log files
    check_log_files()
    
    # Check file permissions
    check_permissions()
    
    print_section("DIAGNOSTIC SUMMARY")
    if cron_running:
        print("✅ Cron service is running")
    else:
        print("❌ Cron service is NOT running - this is a critical issue")
        
    print("\nRecommended actions:")
    print("1. Ensure cron service is running with 'service cron start'")
    print("2. Check that task files in /etc/cron.d/ have proper permissions (0644)")
    print("3. Verify environment variables are loaded correctly in tasks")
    print("4. Check that Python scripts have execute permissions")
    print("5. Review log files for specific error messages")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
