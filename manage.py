import os
import sys
import datetime
from pytz import timezone
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
from autodownload import *
UPDADE_INTERVAL=10
global day
def get_new_data_every(period=UPDADE_INTERVAL):
    # vienna = timezone('Europe/Vienna')
    # day = datetime.now(tz=vienna).day
    day = datetime.now().day
    while True:
        # hour = datetime.now(tz=vienna).hour
        # next_day = datetime.now(tz=vienna).day
        # minute = datetime.now(tz=vienna).minute
        hour = datetime.now().hour
        next_day = datetime.now().day
        minute = datetime.now().minute
        # print(datetime.now(tz=vienna).strftime ("%Y-%m-%d %H:%M:%S"))
        # print("{}>>>>>>>{}".format(next_day-1, day))
        print(datetime.now().strftime ("%Y-%m-%d %H:%M:%S"))
        if next_day - 1 == 0:
            day = 0
        if day == (next_day-1) and hour == 7 and minute == 0:
            download_zip_data()
            day = day + 1
        time.sleep(period)
def start_multi():
    t = threading.Thread(target=get_new_data_every,args=[],daemon=True)
    t.start()
def main():
    start_multi()
    os.chdir("\\home\\stock-management-django\\")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
