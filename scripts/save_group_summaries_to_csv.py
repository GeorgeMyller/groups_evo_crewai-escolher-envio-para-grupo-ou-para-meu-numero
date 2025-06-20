"""
Exporta as tarefas agendadas (resumos de grupos) para data/group_summary.csv
Apenas grupos com resumo agendado são exportados, seguindo o cabeçalho do arquivo.
"""

import os
import sys
import pandas as pd

# Ajusta o caminho do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from whatsapp_manager.core.group_controller import GroupController

OUTPUT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")

CSV_COLUMNS = [
    "group_id", "dias", "horario", "enabled", "is_links", "is_names",
    "send_to_group", "send_to_personal", "script", "start_date", "start_time",
    "end_date", "end_time", "min_messages_summary"
]

def save_group_summaries_to_csv():
    control = GroupController()
    groups = control.fetch_groups()
    if not groups:
        print("Nenhum grupo encontrado para exportar.")
        return

    summary_data = []
    for group in groups:
        # Considera apenas grupos com resumo agendado (enabled=True)
        if getattr(group, 'enabled', False):
            summary_data.append({
                "group_id": getattr(group, 'group_id', ''),
                "dias": getattr(group, 'dias', ''),
                "horario": getattr(group, 'horario', ''),
                "enabled": getattr(group, 'enabled', ''),
                "is_links": getattr(group, 'is_links', ''),
                "is_names": getattr(group, 'is_names', ''),
                "send_to_group": getattr(group, 'send_to_group', ''),
                "send_to_personal": getattr(group, 'send_to_personal', ''),
                "script": getattr(group, 'script', ''),
                "start_date": getattr(group, 'start_date', ''),
                "start_time": getattr(group, 'start_time', ''),
                "end_date": getattr(group, 'end_date', ''),
                "end_time": getattr(group, 'end_time', ''),
                "min_messages_summary": getattr(group, 'min_messages_summary', '')
            })
    if not summary_data:
        print("Nenhum grupo com resumo agendado encontrado.")
        return
    df = pd.DataFrame(summary_data, columns=CSV_COLUMNS)
    df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')
    print(f"Tarefas agendadas salvas em {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    save_group_summaries_to_csv()
