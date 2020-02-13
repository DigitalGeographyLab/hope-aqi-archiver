import time
import traceback
from app.logger import Logger
from app.env_vars import set_env_vars
from app.aqi_fetcher import AqiFetcher
from app.aqi_uploader import AqiUploader
from app.aqi_history_importer import AqiHistoryImporter

log = Logger(b_printing=True, log_file='aqi_archiver.log')
set_env_vars(log)
uploader = AqiUploader(log, aqi_dir='aqi_import/')
fetcher = AqiFetcher(log)
history_importer = AqiHistoryImporter(log, fetcher, uploader, aqi_dir='aqi_import/')
history_importer.import_local_aqi_files()
