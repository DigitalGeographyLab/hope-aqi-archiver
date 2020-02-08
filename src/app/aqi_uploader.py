import os
from os import listdir
import boto3
from app.logger import Logger
from typing import List, Set, Dict, Tuple, Optional

class AqiUploader:
    """AqiUploader can upload air quality index (AQI) data generated by FMI's Enfuser model.

    Attributes:
        log: An instance of Logger class for writing log messages.
        aqi_dir: A filepath pointing to a directory to which AQI files will be temporarily downloaded.
        latest_aqi_upload: The name of the most recently uploaded file.
    """

    def __init__(self, logger: Logger, aqi_dir: str = 'aqi_cache/'):
        self.log = logger
        self.latest_aqi_upload: str = ''
        self.aqi_dir = aqi_dir
        self.aws_access_key_id: str = os.getenv('HOPE_CSC_S3_ACCESS_KEY_ID')
        self.aws_secret_access_key: str = os.getenv('HOPE_CSC_S3_SECRET_ACCESS_KEY')
        self.aws_endpoint: str = os.getenv('HOPE_CSC_S3_ADDRESS')

    def upload_file_to_allas(self, aqi_zip_name: str) -> None:
        self.log.info('uploading aqi_zip to allas...')
        s3_allas = boto3.client(
            's3', 
            region_name='US', 
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.aws_endpoint
            )
        s3_allas.upload_file(self.aqi_dir +'/'+ aqi_zip_name, 'hope-enfuser-archive', aqi_zip_name)
        self.latest_aqi_upload = aqi_zip_name
        self.log.info('uploaded aqi_zip: '+ aqi_zip_name)

    def remove_old_aqi_files(self) -> None:
        """Removes all aqi zip files older than the latest from from aqi_cache.
        """
        rm_count = 0
        error_count = 0
        for file_n in listdir(self.aqi_dir):
            if (file_n.endswith('.zip') and file_n != self.latest_aqi_upload):
                try:
                    os.remove(self.aqi_dir + file_n)
                    rm_count += 1
                except Exception:
                    error_count += 1
                    pass
        self.log.info('removed '+ str(rm_count) +' old AQI zip files')
        if (error_count > 0):
            self.log.warn('could not remove '+ error_count +' old AQI zip files')