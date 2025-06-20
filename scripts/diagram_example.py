"""
Script para gerar um diagrama da arquitetura da codebase do projeto WhatsApp Group Summarizer.
Mostra os principais módulos e suas relações.
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Python
from diagrams.onprem.client import Users
from diagrams.onprem.container import Docker
from diagrams.onprem.database import Mongodb
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.queue import Celery
from diagrams.onprem.vcs import Github

with Diagram("Arquitetura Codebase - WhatsApp Group Summarizer", show=False, filename="diagram_codebase", outformat="png"):
    user = Users("Usuário/CLI/UI")
    github = Github("GitHub Repo")

    with Cluster("src"):
        with Cluster("whatsapp_manager"):
            core = Python("core/")
            utils = Python("utils/")
            ui = Python("ui/")
        scripts = Python("scripts/")
    data = Mongodb("data/")
    docker = Docker("docker/")

    # Relações principais
    user >> ui
    ui >> core
    core >> utils
    core >> data
    scripts >> core
    scripts >> utils
    docker >> core
    docker >> scripts
    github >> [core, utils, ui, scripts, docker]
