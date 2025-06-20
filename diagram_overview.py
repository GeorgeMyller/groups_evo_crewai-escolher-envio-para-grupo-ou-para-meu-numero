from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from diagrams.generic.os import Ubuntu
from diagrams.programming.language import Python
from diagrams.onprem.client import Users
from diagrams.onprem.queue import Celery
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.logging import FluentBit
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis

with Diagram("Groups Evolution CrewAI - Visão Geral", show=False, filename="diagram_overview", direction="TB"):
    user = Users("Usuário/CLI/Streamlit")
    with Cluster("src/whatsapp_manager"):
        with Cluster("core"):
            group_controller = Custom("group_controller.py", "./docs/icons/controller.png")
            group = Custom("group.py", "./docs/icons/group.png")
            summary = Custom("summary.py", "./docs/icons/summary.png")
            send_sandeco = Custom("send_sandeco.py", "./docs/icons/send.png")
            message_sandeco = Custom("message_sandeco.py", "./docs/icons/message.png")
            summary_crew = Custom("summary_crew.py", "./docs/icons/crew.png")
        with Cluster("ui"):
            main_app = Custom("main_app.py", "./docs/icons/app.png")
            page_pt = Custom("2_Portuguese.py", "./docs/icons/pt.png")
            page_en = Custom("3_English.py", "./docs/icons/en.png")
            dashboard = Custom("4_Dashboard.py", "./docs/icons/dashboard.png")
        with Cluster("utils"):
            groups_util = Custom("groups_util.py", "./docs/icons/util.png")
            task_scheduler = Custom("task_scheduler.py", "./docs/icons/scheduler.png")
    data = Custom("data/", "./docs/icons/data.png")
    log = Custom("log_summary.txt", "./docs/icons/log.png")
    docker = Custom("docker/", "./docs/icons/docker.png")
    
    user >> main_app
    main_app >> [page_pt, page_en, dashboard]
    [page_pt, page_en, dashboard] >> group_controller
    group_controller >> [group, summary, send_sandeco, message_sandeco, summary_crew]
    group_controller << groups_util
    summary_crew >> summary
    summary >> send_sandeco
    send_sandeco >> Whatsapp("WhatsApp API")
    group_controller >> data
    summary_crew >> log
    task_scheduler >> summary
    docker >> main_app
    docker >> group_controller
    docker >> summary
    docker >> send_sandeco
    docker >> summary_crew
    docker >> task_scheduler
