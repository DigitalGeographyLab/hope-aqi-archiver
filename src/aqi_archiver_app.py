import time
import traceback
from app.logger import Logger
from app.env_vars import set_env_vars
from app.aqi_fetcher import AqiFetcher
from app.aqi_uploader import AqiUploader
from app.aqi_history_importer import AqiHistoryImporter

log = Logger(b_printing=True, log_file='aqi_archiver.log')
set_env_vars(log)
fetcher = AqiFetcher(log)
uploader = AqiUploader(log)
history_importer = AqiHistoryImporter(log, fetcher, uploader)
if (history_importer.enabled == True):
    history_importer.import_aqi_history()

def download_new_aqi_data():
    expected_aqi_zip_name = fetcher.get_expected_aqi_download_name()
    try:
        fetcher.fetch_enfuser_data(expected_aqi_zip_name)
    except Exception:
        log.error('failed to fetch AQI data: '+ expected_aqi_zip_name)
        traceback.print_exc()
        time.sleep(60)

def upload_new_aqi_data():
    try:
        uploader.upload_file_to_allas(fetcher.latest_aqi_download)
    except Exception:
        log.error('failed to upload AQI data to Allas: '+ fetcher.latest_aqi_download)
        traceback.print_exc()
        time.sleep(60)
    uploader.remove_old_aqi_files()

log.info('starting AQI archiving')
while True:
    if (fetcher.new_aqi_download_available() == True):
        download_new_aqi_data()
    if (uploader.latest_aqi_upload != fetcher.latest_aqi_download):
        upload_new_aqi_data()
    time.sleep(10)
