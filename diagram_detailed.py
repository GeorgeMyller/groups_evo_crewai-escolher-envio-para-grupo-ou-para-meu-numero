from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import Users


with Diagram("Groups Evolution CrewAI - Detalhado", show=False, filename="diagram_detailed", direction="TB"):
    user = Users("Usuário/CLI/Streamlit")
    with Cluster("src/whatsapp_manager"):
        with Cluster("core"):
            group_controller = Custom("group_controller.py", "./docs/icons/controller.png")
            group = Custom("group.py", "./docs/icons/group.png")
            summary = Custom("summary.py", "./docs/icons/summary.png")
            send_sandeco = Custom("send_sandeco.py", "./docs/icons/send.png")
            message_sandeco = Custom("message_sandeco.py", "./docs/icons/message.png")
            summary_crew = Custom("summary_crew.py", "./docs/icons/crew.png")
            summary_lite = Custom("summary_lite.py", "./docs/icons/summary_lite.png")
        with Cluster("ui"):
            main_app = Custom("main_app.py", "./docs/icons/app.png")
            page_pt = Custom("2_Portuguese.py", "./docs/icons/pt.png")
            page_en = Custom("3_English.py", "./docs/icons/en.png")
            dashboard = Custom("4_Dashboard.py", "./docs/icons/dashboard.png")
        with Cluster("utils"):
            groups_util = Custom("groups_util.py", "./docs/icons/util.png")
            task_scheduler = Custom("task_scheduler.py", "./docs/icons/scheduler.png")
    with Cluster("scripts"):
        agendar_todos = Custom("agendar_todos.py", "./docs/icons/script.png")
        save_group_summaries = Custom("save_group_summaries_to_csv.py", "./docs/icons/script.png")
        save_groups = Custom("save_groups_to_csv.py", "./docs/icons/script.png")
    with Cluster("data"):
        data_dir = Custom("data/", "./docs/icons/data.png")
        group_summary = Custom("group_summary.csv", "./docs/icons/csv.png")
        log_summary = Custom("log_summary.txt", "./docs/icons/log.png")
        groups_cache = Custom("groups_cache.json", "./docs/icons/json.png")
    docker = Custom("docker/", "./docs/icons/docker.png")
    # Se não houver Whatsapp, use um Custom genérico
    whatsapp_api = Custom("WhatsApp API", "./docs/icons/whatsapp.png")

    # Usuário e interface
    user >> main_app
    for page in [page_pt, page_en, dashboard]:
        main_app >> page
        page >> group_controller
    # Core
    for mod in [group, summary, send_sandeco, message_sandeco, summary_crew, summary_lite]:
        group_controller >> mod
    groups_util >> group_controller
    summary_crew >> summary
    summary >> send_sandeco
    send_sandeco >> whatsapp_api
    group_controller >> data_dir
    summary_crew >> log_summary
    task_scheduler >> summary
    # Scripts
    agendar_todos >> task_scheduler
    save_group_summaries >> group_controller
    save_group_summaries >> group_summary
    save_groups >> group_controller
    save_groups >> data_dir
    # Data
    for f in [group_summary, log_summary, groups_cache]:
        data_dir >> f
    # Docker
    for mod in [main_app, group_controller, summary, send_sandeco, summary_crew, task_scheduler, agendar_todos, save_group_summaries, save_groups]:
        docker >> mod
