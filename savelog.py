import os
import shutil
from datetime import datetime

def save_log(log_content):
    logs_folder = 'logs'

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

    destination_file = os.path.join(logs_folder, f'{timestamp}.txt')

    print(f"日志内容: {log_content}")

    with open(destination_file, 'w') as f:
        f.write(log_content)

    print(f'日志已保存到 {destination_file}')
