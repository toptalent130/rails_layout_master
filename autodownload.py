import os
import pysftp
import shutil
from autoloadtocsv import *
KNOWN_HOSTS_PATH = 'E:\\Python\\ocm_project\\app\\ocm_data\\known_hosts.txt'
SFTP_HOSTNAME = 'sftp.datashop.livevol.com'  # 'sftp2.datashop.livevol.com'
SFTP_USERNAME = 'biros_michael_gmail_com'
SFTP_PASSWORD = 'Mikelik77--'
PATH_TO_ORDER_FILES = '/subscriptions/order_000017853/item_000021925'
LOCAL_DIR_PATH = 'E:\\Python\\ocm_project\\app\\ocm_data\\data\\SPX\\CBOE\\'
IMPORT_DIR_PATH = 'E:\\Python\\ocm_project\\app\\ocm_data\\data\\SPX\\ToImport\\'

def download_zip_data():
    os.chdir(LOCAL_DIR_PATH)
    print('Auto downloading zip files ...')
    try:
        cnopts = pysftp.CnOpts(knownhosts=KNOWN_HOSTS_PATH)
        with pysftp.Connection(SFTP_HOSTNAME, username=SFTP_USERNAME, password=SFTP_PASSWORD, cnopts=cnopts) as sftp:
            with sftp.cd(PATH_TO_ORDER_FILES):  # temporarily change directory
                for file_name in sftp.listdir():  # list all files in directory
                    if not os.path.isfile(file_name):
                        sftp.get(file_name, localpath=os.path.join(LOCAL_DIR_PATH, file_name))  # get a remote file
                        print('File {} downloaded to archive.'.format(file_name))
                        shutil.copy(file_name,IMPORT_DIR_PATH) 
                        print('File {} copied to ToImport.'.format(file_name))
    except:
        print("AuthenticationException araised")
    print('Auto downloading done')
    autoload()
