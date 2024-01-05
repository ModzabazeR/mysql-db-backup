import os
import re
import time
import subprocess
from dotenv import load_dotenv

# load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# relative path
backup_dir = "backups"
date_format = '%Y-%m-%d_%H-%M-%S'

# every 1 hour
BACKUP_INTERVAL = 60 * 60

# create backup directory if it doesn't exist
backup_file_path = f"{backup_dir}/latest_backup.sql"
if not os.path.exists(backup_file_path):
    open(backup_file_path, 'w').close()
previous_backup_content = open(backup_file_path, 'r').read()

while True:
    # get current time
    current_time = time.strftime(date_format)

    # create backup file name
    backup_file_name = f"{DB_NAME}_{current_time}.sql"

    # create backup file path
    backup_file_path = os.path.join(backup_dir, backup_file_name)

    # create backup command
    # execute backup command and capture the output
    backup_command = f'mysqldump -h {DB_HOST} -u {DB_USER} -p"{DB_PASS}" {DB_NAME}'
    backup_output = subprocess.check_output(backup_command, shell=True, universal_newlines=True, stderr=subprocess.DEVNULL)
    backup_output = re.sub(r'-- Dump completed on.*\n', '', backup_output)

    current_backup_content = backup_output

    color = "\033[92m" # green

    if current_backup_content != previous_backup_content:
        color = "\033[91m" # red
        print(f"{current_time} - status: {color}File contents are differ\033[0m")

        with open(f"{backup_dir}/latest_backup.sql", 'w') as f:
            f.write(current_backup_content)

        with open(backup_file_path, 'w') as f:
            f.write(current_backup_content)

        # compress backup file
        gzip_command = f"gzip {backup_file_path}"
        os.system(gzip_command)

        # delete backup that are 7 days old
        delete_command = f"find {backup_dir} -type f -name '*.gz' -mtime +7 -exec rm {{}} \;"
        os.system(delete_command)

        # update previous backup hash
        previous_backup_content = current_backup_content
    else:
        # delete duplicate backup file
        color = "\033[92m" # green
        print(f"{current_time} - status: {color}File contents are the same\033[0m")

    # wait for next backup
    time.sleep(BACKUP_INTERVAL)