import os
from typing import Dict
from appdirs import user_data_dir

def get_save_directory():
    """Finds the directory where user data should be stored"""
    APPNAME = "redyoinker"
    APPAUTHOR = "MaxensDestine"
    dir = user_data_dir(APPNAME, APPAUTHOR)
    if not os.path.exists(dir):
        os.makedirs(dir)

    return dir.rstrip("/")

def my_print(msg: str):
    display_logs
    if display_logs:
        print(msg)


# max request per minute for each domain
# domains other than the first 3 are rarely used, so we can use an absurb rate
dic_request_limit: Dict[str, int] = {"pushshift":60, "reddit":60, "imgur":60, "any": 9999999}

# A maximum of 100 results is returned by the pushshift API for any given requests. This variable should only be changed if they change their API
max_nb_results: int = 100

maxrepeat: int = 3
timeout: int = 5
display_logs: bool = False
datadir: str = ""
datadir = get_save_directory()

total_nb_submissions: int = 0
nb_of_processed_submissions: int = 0
done_getting_submissions = False
all_submissions: list = []