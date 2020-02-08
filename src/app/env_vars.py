import os
import csv

def set_env_vars():
    try:
        with open('.env', newline='') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['key', 'value'], delimiter='=')
            for row in reader:
                os.environ[row['key']] = row['value']
    except Exception:
        print('no .env file found')
        pass
