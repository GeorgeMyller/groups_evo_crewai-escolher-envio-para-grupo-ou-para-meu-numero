from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.programming.language import Python
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github
from diagrams.onprem.container import Docker
from diagrams.onprem.database import Mongodb
from diagrams.generic.storage import Storage

with Diagram("Arquitetura Codebase Detalhada - WhatsApp Group Summarizer", show=False, filename="diagram_codebase_detalhado", direction="LR"):
    user = Users("Usuário/CLI/UI")
    github = Github("GitHub Repo")
    docker = Docker("Docker")
    mongo = Mongodb("MongoDB (data/)")
    
    with Cluster("src/whatsapp_manager"):
        with Cluster("ui"):
            ui_interface = Python("interface.py")
        with Cluster("core"):
            core_main = Python("main.py")
            core_scheduler = Python("scheduler.py")
        with Cluster("utils"):
            utils_helpers = Python("helpers.py")
    
    with Cluster("scripts"):
        script_list_tasks = Python("list_scheduled_tasks.py")
    
    with Cluster("data"):
        group_summary = Storage("group_summary.csv")
        log_summary = Storage("log_summary.txt")
        with Cluster("cache"):
            cache_icons = Storage("custom_icons/")
    
    
    # Fluxos principais
    user >> ui_interface
    ui_interface >> core_main
    core_main >> core_scheduler
    core_scheduler >> utils_helpers
    core_scheduler >> group_summary
    core_scheduler >> log_summary
    core_scheduler >> cache_icons
    script_list_tasks >> core_scheduler
    script_list_tasks >> group_summary
    script_list_tasks >> log_summary
    group_summary >> mongo
    log_summary >> mongo
    docker >> [ui_interface, core_main, core_scheduler, script_list_tasks, mongo]
    github >> docker
