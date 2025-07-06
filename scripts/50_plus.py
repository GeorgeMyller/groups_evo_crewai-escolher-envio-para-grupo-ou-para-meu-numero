import argparse
import csv
import os
import sys
from datetime import datetime, timedelta

# Determine project root relative to this script file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from whatsapp_manager.core.group_controller import GroupController
from whatsapp_manager.utils.task_scheduler import TaskScheduled

def main():
    parser = argparse.ArgumentParser(
        description="Agenda resumo diário para todos os grupos (envio para seu número pessoal)"
    )
    parser.add_argument('--time', type=str, default='21:00', help='Horário do agendamento no formato HH:MM (padrão: 21:00)')
    parser.add_argument('--group-scan-time', type=str, default='20:50', help='Horário para buscar novos grupos diariamente (padrão: 20:50)')
    args = parser.parse_args()

    summary_script_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")
    group_info_csv_path = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
    if not os.path.exists(group_info_csv_path):
        group_info_csv_path = os.path.join(PROJECT_ROOT, "group_summary.csv")

    if not os.path.exists(group_info_csv_path):
        print(f"Erro: Arquivo group_summary.csv não encontrado em {group_info_csv_path}")
        sys.exit(1)

    if not os.path.exists(summary_script_path):
        print(f"Erro: Script summary.py não encontrado em {summary_script_path}")
        sys.exit(1)

    # Adiciona agendamento para buscar novos grupos uma vez ao dia
    group_scan_script_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "scan_groups.py")
    if os.path.exists(group_scan_script_path):
        TaskScheduled.create_task(
            task_name='BuscarNovosGrupos',
            python_script_path=group_scan_script_path,
            schedule_type='DAILY',
            time=args.group_scan_time,
        )
        print(f"Agendamento diário para buscar novos grupos às {args.group_scan_time}")
    else:
        print(f"Aviso: Script scan_groups.py não encontrado em {group_scan_script_path}. Busca diária de grupos não agendada.")

    try:
        with open(group_info_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            control = GroupController()
            # Parse initial time
            current_time = datetime.strptime(args.time, "%H:%M")
            idx = 0
            for row in reader:
                group_id = row.get('group_id')
                message_count = int(row.get('message_count', 0))
                if not group_id:
                    print(f"Aviso: Linha ignorada em group_summary.csv por falta de group_id: {row}")
                    continue
                if message_count <= 50:
                    print(f"Grupo {group_id} ignorado (apenas {message_count} mensagens).")
                    continue

                # Calcula o horário para este grupo
                scheduled_time = (current_time + timedelta(minutes=idx)).strftime("%H:%M")

                print(f"Agendando para o grupo: {group_id} às {scheduled_time}")
                control.update_summary(
                    group_id=group_id,
                    horario=scheduled_time,
                    enabled=True,
                    is_links=True,
                    is_names=True,
                    script=summary_script_path,
                    send_to_group=False,
                    send_to_personal=True
                )
                TaskScheduled.create_task(
                    task_name=f'ResumoGrupo_{group_id}',
                    python_script_path=summary_script_path,
                    schedule_type='DAILY',
                    time=scheduled_time,
                )
                idx += 1
        print(f'Agendamento diário para todos os grupos realizado! (envio para seu número pessoal, início: {args.time}, intervalo de 1 minuto)')
    except FileNotFoundError:
        print(f"Erro: O arquivo {group_info_csv_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")
