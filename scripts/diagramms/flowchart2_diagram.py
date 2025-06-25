from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import User
from diagrams.programming.language import Python
from diagrams.onprem.compute import Server
from diagrams.gcp.iot import IotCore
from diagrams.onprem.network import Internet
from diagrams.onprem.logging import FluentBit


with Diagram(
    "Fluxo de Alto Nível - Interface até Log (Com Nodes da Docs)",
    show=False,
    filename="flowchart2_diagram_doc_nodes",
    outformat="png",
    direction="LR"  # Mudança para layout horizontal
):
    # Cluster do Front-end
    with Cluster("👤 Usuário"):
        interface = User("Streamlit\n2_Portuguese.py\n3_English.py")

    # Cluster dos Serviços de Backend
    with Cluster("⚙️ Backend"):
        agendamento = Python("⏰\nAgendamento\ntask_scheduler.py")
        resumo = Python("📄\nResumo\nsummary.py")
        coleta = Server("📥\nColeta\ngroup_controller.py")
        gera_resumo = IotCore("🤖\nIA Resumo\nsummary_crew.py")
        envia = Internet("🌐\nEnvia\nsend_sandeco.py")

    # Cluster de Persistência/Output
    with Cluster("🗄️ Logs & Output"):
        log = FluentBit("📝\nLog\nlog_summary.txt")

    # Conexões
    _ = interface >> Edge(
        label="\n   💾  Salva & Agenda   \n",
        color="darkgreen",
        style="dashed"
    ) >> agendamento

    _ = agendamento >> Edge(
        label="\n   ⏱️  Executa   \n",
        color="blue"
    ) >> resumo

    _ = resumo >> Edge(
        label="\n   🔄  Processa   \n",
        color="purple"
    ) >> coleta

    _ = coleta >> Edge(
        label="\n   🧠  Gera Resumo   \n",
        color="orange"
    ) >> gera_resumo

    _ = gera_resumo >> Edge(
        label="\n   📤  Envia   \n",
        color="red"
    ) >> envia

    _ = envia >> Edge(
        label="\n   📝  Log   \n",
        color="brown"
    ) >> log