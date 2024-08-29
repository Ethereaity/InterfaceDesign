import os
import shutil
from datetime import datetime


def save_log(log_content):
    logs_folder = 'logs'

    # 创建目标文件夹（如果不存在的话）
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # 获取当前日期和时间
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

    # 定义目标文件路径
    destination_file = os.path.join(logs_folder, f'{timestamp}.txt')

    # 打印日志内容用于调试
    print(f"日志内容: {log_content}")

    # 写入日志内容到文件
    with open(destination_file, 'w') as f:
        f.write(log_content)

    print(f'日志已保存到 {destination_file}')