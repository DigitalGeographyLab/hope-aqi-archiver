import os
import csv
from app.logger import Logger

def set_env_vars(log: Logger):
    try:
        with open('.env', newline='') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['key', 'value'], delimiter='=')
            for row in reader:
                os.environ[row['key']] = row['value']
    except Exception:
        log.warning('no .env file found')
        pass
