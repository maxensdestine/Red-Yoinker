import os
from io import TextIOWrapper
from mediadownloader import download_from_url
from typing import Dict, List
from configs import datadir
from datetime import datetime


sub_to_ids: Dict[str, List[str]] = None
file_ptrs: Dict[str, TextIOWrapper] = None
history_file_name_end = str("_history.txt")
failure_file_name_end = str("_failure.txt")


def submission_is_in_history(submission: dict) -> bool:
    subreddit = str(submission.get("subreddit"))
    id = str(submission.get("id"))
    subreddit_history_exists = bool(sub_to_ids.get(subreddit))
    id_is_in_history = bool(id in sub_to_ids.get(subreddit))

    return subreddit_history_exists and id_is_in_history



def add_to_failure(submission: dict):
    """Add the failed media url to the corresponding failure file (separated by subreddit)"""

    subreddit = str(submission.get("subreddit"))
    id = str(submission.get("id"))
    link = str(submission.get("full_link"))
    title = str(submission.get("title"))
    date = str(datetime.fromtimestamp(float(submission.get("created_utc"))))
    line = id + "," + link + "," + title + "," + date + "\n"
    with open(os.path.join(datadir, subreddit + failure_file_name_end), "a") as file:
        file.write(line)



def show_failures(subreddits: List[str]):
    """Displays the name of subreddits which have failures associated to them and the number of failures"""

    print("For your information, failure files are stored at: " + datadir)

    del_all = not bool(subreddits)
    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(failure_file_name_end)]

    if not del_all:
        onlyfiles = [f for f in onlyfiles if f.split(failure_file_name_end)[0] in subreddits]

    if  onlyfiles:
        for f in os.listdir(datadir):
            if os.path.isfile(os.path.join(datadir, f)) and f.endswith(failure_file_name_end):
                with open(os.path.join(datadir, f), "r") as file:
                    nb_lines = len(file.readlines())

                print(f.split(failure_file_name_end)[0] + ": " + str(nb_lines) + " failures")
    else:
        print("No failure file was found")



def clear_failures(subreddits: List[str]):
    """Deletes the failure files of the given subreddits"""

    del_all = not bool(subreddits)
    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(failure_file_name_end)]

    if not del_all:
        onlyfiles = [f for f in onlyfiles if f.split(failure_file_name_end)[0] in subreddits]

    if onlyfiles:
        for f in onlyfiles:
            os.remove(os.path.join(datadir, f))
            subreddit = f.split(failure_file_name_end)[0]
            print("Deleted the failure file of subreddit: " + subreddit)
    else:
        print("No failure file was found")




def add_to_history(submission: dict):
    """Adds the submission id, link, title to the respective history file (separated by subreddit)"""

    subreddit = str(submission.get("subreddit"))
    id = str(submission.get("id"))
    link = str(submission.get("full_link"))
    title = str(submission.get("title"))
    date = str(datetime.fromtimestamp(float(submission.get("created_utc"))))
    line = id + "," + link + "," + title + "," + date + "\n"
    if file_ptrs.get(subreddit):
        file_ptrs.get(subreddit).write(line)
    else:
        open(os.path.join(datadir, subreddit + history_file_name_end), "a").write(line)



def clear_history(subreddits: List[str]):
    """Deletes the history files of the given subreddits"""

    del_all = not bool(subreddits)
    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(history_file_name_end)]
    
    if not del_all:
        onlyfiles = [f for f in onlyfiles if f.split(history_file_name_end)[0] in subreddits]

    if onlyfiles:
        for f in onlyfiles:
            os.remove(os.path.join(datadir, f))
            subreddit = f.split(history_file_name_end)[0]
            print("Deleted the history file of subreddit: " + subreddit)
    else:
        print("No history file was found")



def show_history(subreddits: List[str]):
    """Displays the names of all subreddits which have history files"""

    print("For your information, history files are stored at: " + datadir)

    del_all = not bool(subreddits)
    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(history_file_name_end)]

    if not del_all:
        onlyfiles = [f for f in onlyfiles if f.split(history_file_name_end)[0] in subreddits]

    if  onlyfiles:
        for f in os.listdir(datadir):
            if os.path.isfile(os.path.join(datadir, f)) and f.endswith(history_file_name_end):
                with open(os.path.join(datadir, f), "r") as file:
                    nb_lines = len(file.readlines())

                print(f.split(history_file_name_end)[0] + ": " + str(nb_lines) + " submissions")
    else:
        print("No history file was found")



def retry_failures(subreddits: List[str]):
    """Tries to re download media from the given subreddits' failure files. Will retry for all failure files if the del_all parameter is True"""
    
    del_all = bool(subreddits)
    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(failure_file_name_end)]

    if not del_all:
        onlyfiles = [f for f in onlyfiles if f.split(failure_file_name_end)[0] in subreddits]

    for f in onlyfiles:
        retry_failures_subreddit(f.split(failure_file_name_end)[0])



def retry_failures_subreddit(subreddit: str):
    """ Tries to redownload media from the given subreddit's failure file"""

    still_failures: list[str] = []
    path = os.path.join(datadir, subreddit + failure_file_name_end)
    final_len = 1

    if not os.path.exists(path):
        return

    with open(path, "r") as file:
        lines = file.readlines()
        init_len = len(lines)
        for i in range(0, init_len):
            print("Retry " + str(i) + "/" + str(init_len), end = "\r")
            line = lines[i]
            url = line.split(",")[0]
            title = line.split(",")[-1]
            is_success = download_from_url(url, title)
            if not is_success:
                still_failures.append(line)
        
        final_len = len(still_failures)
        diff = init_len - final_len
        print("Retry " + str(init_len) + "/" + str(init_len))
        print("For " + subreddit + ": ")
        print("Number of downloads that previously failed but were successful this time: " + str(diff))
        print("Remaining failing downloads:" + str(final_len))

    if final_len == 0:
        # if there are no failures, we delete the file
        os.remove(path)
    # truncate the file and write the urls that failed again
    with open(path, "w") as file:
        file.writelines(still_failures)



def get_history_ptr(subreddits: List[str]):
    """return a dictionary which contains a TextIOWrapper obj for each given subreddit. The IOWrapper is intended to be used to write to the history file of the given subreddit"""

    file_ptrs: Dict[str, TextIOWrapper] = {}
    # prepare file pointers in advance if we know we will need it(faster than creating one every time)
    for sub in subreddits:
        file = os.path.join(datadir, sub + history_file_name_end)
        file_ptrs[sub] = open(file, "a")
    
    return file_ptrs



def load_history(subreddits: List[str]):
    """returns the ids from the history files. Only the ids of the given subreddits will be included"""

    sub_to_ids: Dict[str, List[str]] = {}

    for sub in subreddits:
        sub_to_ids[sub] = []

    onlyfiles = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f)) and f.endswith(history_file_name_end)]
    
    for f in onlyfiles:
        sub = f.split(history_file_name_end)[0]
        #only load the history of subreddits we are looking for
        file = os.path.join(datadir, sub + history_file_name_end)
        if sub in subreddits:
            ids = [x.split(",")[0] for x in open(file).readlines()]
            sub_to_ids[sub] = ids
    
    return sub_to_ids


        
def initialize_history(subreddits: List[str]):
    global file_ptrs
    global sub_to_ids
    sub_to_ids = load_history(subreddits)
    file_ptrs = get_history_ptr(subreddits)