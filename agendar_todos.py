import csv
import os
import argparse
from group_controller import GroupController
from task_scheduler import TaskScheduled

parser = argparse.ArgumentParser(description="Agenda resumo diário para todos os grupos (envio para seu número pessoal)")
parser.add_argument('--time', type=str, default='21:00', help='Horário do agendamento no formato HH:MM (padrão: 21:00)')
args = parser.parse_args()

summary_path = os.path.join(os.getcwd(), 'summary.py')

with open('group_info.csv') as f:
    reader = csv.DictReader(f)
    control = GroupController()
    for row in reader:
        group_id = row['group_id']
        control.update_summary(
            group_id=group_id,
            horario=args.time,
            enabled=True,
            is_links=True,
            is_names=True,
            script=summary_path,
            send_to_group=False,
            send_to_personal=True
        )
        TaskScheduled.create_task(
            f'ResumoGrupo_{group_id}',
            summary_path,
            schedule_type='DAILY',
            time=args.time,
        )
print(f'Agendamento diário para todos os grupos realizado! (envio para seu número pessoal, horário: {args.time})')
