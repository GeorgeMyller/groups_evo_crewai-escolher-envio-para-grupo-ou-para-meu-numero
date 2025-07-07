# Docker Task Scheduler Fix

This document explains the changes made to fix the task scheduling issues in Docker containers, specifically to address the problem where scheduled tasks were working via CLI but not visible or manageable through the Streamlit interface.

## Problem Summary

1. **Original Issue**: 
   - In Docker, scheduling worked via CLI but the Streamlit UI couldn't show or manage scheduled tasks.
   - This was because the Docker implementation of task scheduling used a different approach than the standard implementation, but the Streamlit UI wasn't correctly interfacing with it.

2. **Root Causes**:
   - Docker environment detection was incomplete
   - Docker-specific task scheduler wasn't properly integrated with the clean architecture version
   - Streamlit UI was not correctly listing tasks created in Docker environment

## Implemented Solutions

### 1. Docker Environment Detection

Added improved Docker detection in `task_scheduler.py`:
- Checks for Docker-specific files and environment variables
- Identifies Docker container by directory structure
- Detects supervisord running (typical in Docker setup)

### 2. Docker Task Scheduler Implementation 

Created a dedicated Docker task scheduler in `docker_task_scheduler.py`:
- Implements a clean, object-oriented approach consistent with the architecture
- Uses `/etc/cron.d/` files instead of user crontab for more reliable scheduling
- Adds proper logging for debugging
- Implements consistent API with the main TaskSchedulingService

### 3. TaskSchedulingService Integration

Updated `TaskSchedulingService` to use Docker scheduler when appropriate:
- Auto-detects Docker environment
- Delegates to Docker-specific implementation when in Docker
- Maintains consistent API for backwards compatibility
- Supports additional features like script arguments

### 4. Diagnostic and Testing Tools

Added diagnostic and testing tools:
- `diagnose_docker_scheduling.py`: Checks cron service, files, permissions, and logs
- `test_docker_scheduler.py`: Tests creation, listing, and deletion of scheduled tasks

## How to Use

### For Normal Operation

1. Start the Clean Architecture Streamlit app:
   ```
   uv run streamlit run src_clean/whatsapp_manager/presentation/web/main_app.py
   ```

2. The system will now correctly detect Docker environments and use the appropriate scheduling mechanism.

3. Tasks scheduled through Streamlit will now be visible and manageable in the UI even in Docker environments.

### For Troubleshooting

If you encounter issues with task scheduling in Docker:

1. Run the diagnostic tool:
   ```
   python tools/diagnose_docker_scheduling.py
   ```

2. Test the scheduler functionality:
   ```
   python tools/test_docker_scheduler.py
   ```

3. Check logs in `/app/data/`:
   - `docker_scheduler.log`: Docker-specific scheduling logs
   - `cron_scheduling.log`: Task creation/deletion logs
   - `cron_monitor.log`: Cron service monitoring logs
   - `task_*.log`: Individual task execution logs

## Technical Details

### File Structure

- **src_clean/whatsapp_manager/infrastructure/scheduling/task_scheduler.py**
  - Main cross-platform scheduler with Docker detection
  
- **src_clean/whatsapp_manager/infrastructure/scheduling/docker_task_scheduler.py**
  - Docker-specific implementation
  
- **tools/diagnose_docker_scheduling.py**
  - Diagnostic tool for Docker scheduling issues
  
- **tools/test_docker_scheduler.py**
  - Testing tool for Docker scheduler functionality

### Docker Task Scheduling Process

1. **Task Creation**:
   - Task name and script path provided
   - Creates a file in `/etc/cron.d/` with proper permissions
   - Uses environment loader script to ensure environment variables
   - Records detailed logs of scheduling operations

2. **Task Listing**:
   - Lists all tasks from `/etc/cron.d/` files
   - Also checks user crontab for backward compatibility
   - Returns structured data about each task

3. **Task Deletion**:
   - Removes task file from `/etc/cron.d/`
   - Also tries crontab for backward compatibility
   - Logs deletion operations

## Additional Notes

- The system now properly handles both `DAILY` and `ONCE` schedule types in Docker
- All operations are logged for easier troubleshooting
- Docker detection is robust against different Docker configurations
- The scheduler automatically handles file permissions for cron files
