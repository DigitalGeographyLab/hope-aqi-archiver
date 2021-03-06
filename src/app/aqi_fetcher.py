import os
from datetime import datetime
import boto3
from app.logger import Logger
from typing import List, Set, Dict, Tuple, Optional

class AqiFetcher:
    """AqiFetcher can download air quality index (AQI) data generated by FMI's Enfuser model.

    Attributes:
        log: An instance of Logger class for writing log messages.
        aqi_dir: A filepath pointing to a directory to which AQI files will be temporarily downloaded.
        latest_aqi_download: The name of the most recently downloaded file.
    """

    def __init__(self, logger: Logger, aqi_dir: str = 'aqi_cache/'):
        self.log = logger
        self.aqi_dir = aqi_dir
        self.latest_aqi_download: str = ''
        self.s3_enfuser_data_folder = 'Finland/pks/'
        self.s3_bucketname: str = 'enfusernow2'
        self.s3_region: str = 'eu-central-1'
        self.aws_access_key_id: str = os.getenv('ENFUSER_S3_ACCESS_KEY_ID')
        self.aws_secret_access_key: str = os.getenv('ENFUSER_S3_SECRET_ACCESS_KEY')

    def get_expected_aqi_download_name(self) -> str:
        """Returns the name of the latest expected aqi zip file.
        """
        curdt = datetime.utcnow().strftime('%Y-%m-%dT%H')
        aqi_zip_name = 'allPollutants_' + curdt + '.zip'
        return aqi_zip_name

    def new_aqi_download_available(self) -> bool:
        """Returns False if the expected latest aqi file is either already downloaded or currently being downloaded, 
        else returns True.
        """
        return self.latest_aqi_download != self.get_expected_aqi_download_name()

    def fetch_enfuser_data(self, aqi_zip_name: str) -> None:
        """Downloads the current enfuser data as a zip file containing multiple netcdf files to the aqi_cache directory. 
        
        Returns:
            The name of the downloaded zip file (e.g. allPollutants_2019-11-08T14.zip).
        """
        self.log.info('fetching '+ aqi_zip_name +'...')
        # connect to S3
        s3 = boto3.client('s3',
                        region_name=self.s3_region,
                        aws_access_key_id=self.aws_access_key_id,
                        aws_secret_access_key=self.aws_secret_access_key
                        )
                
        # download the netcdf file to a specified location
        file_out = self.aqi_dir + '/' + aqi_zip_name
        s3.download_file(self.s3_bucketname, self.s3_enfuser_data_folder + aqi_zip_name, file_out)
        self.log.info('fetch done')
        self.latest_aqi_download = aqi_zip_name

    def get_available_files_list(self) -> list:
        s3 = boto3.client('s3',
                        region_name=self.s3_region,
                        aws_access_key_id=self.aws_access_key_id,
                        aws_secret_access_key=self.aws_secret_access_key
                        )

        available_files = []
        try:
            for key in s3.list_objects_v2(Bucket=self.s3_bucketname)['Contents']:
                if (key['Key'].startswith('Finland/pks/allPollutants') and key['Key'].endswith('.zip')):
                    available_files.append(key['Key'][12:])
        except Exception:
            self.log.warning('could not retreive list of objects, possibly empty bucket')

        return available_files
