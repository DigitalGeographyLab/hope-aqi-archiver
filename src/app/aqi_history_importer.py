import os
import time
from datetime import datetime, timedelta
from app.logger import Logger
from app.aqi_fetcher import AqiFetcher
from app.aqi_uploader import AqiUploader
from typing import List, Set, Dict, Tuple, Optional

class AqiHistoryImporter:

    def __init__(self, logger: Logger, fetcher: AqiFetcher, uploader: AqiUploader, aqi_dir: str = 'aqi_cache/'):
        self.enabled = bool(os.getenv('HISTORY_IMPORT_ENABLED')) if 'HISTORY_IMPORT_ENABLED' in os.environ else False
        self.from_time = os.getenv('HISTORY_IMPORT_FROM_TIME') # e.g. 2019-12-30T05
        self.log = logger
        self.aqi_dir = aqi_dir
        self.fetcher = fetcher
        self.uploader = uploader
        self.to_fetch: list = []
        self.fetched: list = []
        self.uploaded: list = []

    def import_aqi_history(self) -> None:
        self.log.info('starting AQI import from: '+ self.from_time)
        self.collect_to_fetch_list()
        if (len(self.to_fetch) > 0):
            self.fetch_upload()

    def import_local_aqi_files(self) -> None:
        to_import = [fn for fn in os.listdir(self.aqi_dir) if ('.zip' in fn)]
        self.log.info('uploading '+ str(len(to_import)) +' files')
        for file_import in to_import:
            try:
                self.uploader.upload_file_to_allas(file_import)
                os.remove(self.aqi_dir + file_import)
            except Exception:
                self.log.error('failed to upload: '+ file_import)
                time.sleep(2)
        self.log.info('all files uploaded')

    def collect_to_fetch_list(self) -> None:
        fetch_time = datetime.strptime(self.from_time, '%Y-%m-%dT%H')
        
        while fetch_time <= datetime.utcnow():
            self.to_fetch.append('allPollutants_' + fetch_time.strftime('%Y-%m-%dT%H') + '.zip')
            fetch_time += timedelta(hours=1)
        self.log.info('initial to import count: '+ str(len(self.to_fetch)))

        # filter out already uploaded files
        uploaded = self.uploader.get_uploaded_files_list()
        self.log.info('already uploaded count: '+ str(len([to_fetch for to_fetch in self.to_fetch if to_fetch in uploaded])))
        self.to_fetch = [to_fetch for to_fetch in self.to_fetch if to_fetch not in uploaded]

        # filter out unavailable files
        if (len(self.to_fetch) > 0):
            available = self.fetcher.get_available_files_list()
            self.log.info('available to import count: '+ str(len([to_fetch for to_fetch in self.to_fetch if to_fetch in available])))
            self.log.info('unavailable to import count: '+str(len([to_fetch for to_fetch in self.to_fetch if to_fetch not in available])))
            self.to_fetch = [to_fetch for to_fetch in self.to_fetch if to_fetch in available]

    def fetch_upload(self) -> None:
        for aqi_file in self.to_fetch:
            # fetch
            for attempt in range(3):
                try:
                    self.fetcher.fetch_enfuser_data(aqi_file)
                    self.fetched.append(aqi_file)
                except Exception:
                    self.log.error('error in fetching: '+ aqi_file)
                    time.sleep(attempt*7)
                    continue
                break
            # upload
            if (aqi_file in self.fetched):
                for attempt in range(3):
                    try:
                        self.uploader.upload_file_to_allas(aqi_file)
                        self.uploaded.append(aqi_file)
                    except Exception:
                        self.log.error('error in uploading: '+ aqi_file)
                        time.sleep(attempt*7)
                        continue
                    break
            # delete cached file
            if (aqi_file in self.fetched):
                try:
                    os.remove(self.aqi_dir + aqi_file)
                except Exception:
                    self.log.warning('could not remove cached file: '+ aqi_file)
        
        self.log.info('imported '+ str(len(self.uploaded)) + ' of '+ str(len(self.to_fetch)) + ' files')
