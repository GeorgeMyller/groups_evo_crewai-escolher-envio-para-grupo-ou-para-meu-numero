import argparse
import csv
import os
import sys

# Determine project root relative to this script file (scripts/agendar_todos.py -> ../ -> project_root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from whatsapp_manager.core.group_controller import GroupController
from whatsapp_manager.utils.task_scheduler import TaskScheduled

parser = argparse.ArgumentParser(description="Agenda resumo diário para todos os grupos (envio para seu número pessoal)")
parser.add_argument('--time', type=str, default='21:00', help='Horário do agendamento no formato HH:MM (padrão: 21:00)')
args = parser.parse_args()

# Corrected paths relative to PROJECT_ROOT
summary_script_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")
group_info_csv_path = os.path.join(PROJECT_ROOT, "data", "group_info.csv")

if not os.path.exists(group_info_csv_path):
    print(f"Erro: Arquivo group_info.csv não encontrado em {group_info_csv_path}")
    sys.exit(1)

if not os.path.exists(summary_script_path):
    print(f"Erro: Script summary.py não encontrado em {summary_script_path}")
    sys.exit(1)

try:
    with open(group_info_csv_path, mode='r', encoding='utf-8') as f: # Added mode and encoding
        reader = csv.DictReader(f)
        control = GroupController() # Assumes .env is loaded correctly by GroupController from PROJECT_ROOT
        for row in reader:
            group_id = row.get('group_id')
            if not group_id:
                print(f"Aviso: Linha ignorada em group_info.csv por falta de group_id: {row}")
                continue

            print(f"Agendando para o grupo: {group_id} às {args.time}")
            control.update_summary(
                group_id=group_id,
                horario=args.time,
                enabled=True,
                is_links=True,
                is_names=True,
                script=summary_script_path,
                send_to_group=False,
                send_to_personal=True
            )
            TaskScheduled.create_task(
                task_name=f'ResumoGrupo_{group_id}', # Consistent with Portuguese version of UI
                python_script_path=summary_script_path,
                schedule_type='DAILY',
                time=args.time,
            )
    print(f'Agendamento diário para todos os grupos realizado! (envio para seu número pessoal, horário: {args.time})')
except FileNotFoundError:
    print(f"Erro: O arquivo {group_info_csv_path} não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro durante o processamento: {e}")
