import time
import traceback
from datetime import datetime
from app.aqi_archiver import AqiArchiver
from app.logger import Logger

log = Logger(b_printing=True, log_file='aqi_archiver.log')
AQI = AqiArchiver(log, set_aws_secrets=True)

def process_new_aqi_data():
    expected_aqi_zip_name = AQI.get_expected_aqi_download_name()
    AQI.set_wip_aqi_download_name(expected_aqi_zip_name)
    try:
        log.info('fetching Enfuser data...')
        aqi_zip_name = AQI.fetch_enfuser_data(expected_aqi_zip_name)
        log.info('downloaded aqi_zip: '+ aqi_zip_name)
    except Exception:
        log.error('failed to download AQI data: '+ AQI.wip_aqi_download)
        traceback.print_exc()
        time.sleep(45)
    finally:
        AQI.remove_old_aqi_files()
        AQI.reset_wip_aqi_download_name()

log.info('starting AQI archiving')

while True:
    if (AQI.new_aqi_download_available() == True):
        process_new_aqi_data()
    time.sleep(10)
