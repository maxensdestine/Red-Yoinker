import configs, historyandfailure, submissionhandler
from requests import get
from time import sleep
from sys import exit
from signal import signal, SIGINT
from argumentparser import parse_arguments
from copy import deepcopy
from typing import Iterable, Union
from ratelimit import limits, sleep_and_retry
from threading import Thread


def count_elements_in_iterable(iterable)->int:
    return int(sum(1 for _ in iterable))



def get_last_from_iterable(iterable: Iterable):
    *_, last = iterable
    return last



@sleep_and_retry
@limits(calls=configs.dic_request_limit["pushshift"], period=60)
def send_pushshift_req(func):
    return func()



def get_pushshift_request(my_url: str, params: dict):
    """Get a request from the given url. Loops until the request returns 200 ok and return null if the maximum number of retries has been reached"""

    data = None
    my_func = lambda: get(url=my_url, params=params)
    for _ in range(0, configs.maxrepeat):
        response = send_pushshift_req(func=my_func)
        configs.my_print("Sending pushshift request: [" + response.url + "]")
        try:
            if response.status_code == 200:
                data = response.json()['data']
                break
            else:
                raise Exception
        except Exception:
            sleep_time = float(response.headers.get('Retry-After', configs.timeout))
            sleep(sleep_time)
            continue
    return response, data



def get_pushshift_submissions(params: dict):
    """Get submissions from the pushshift API using the given parameters (dictionary of lists)"""
    submissions_endpoint = "https://api.pushshift.io/reddit/search/submission/"
    return get_pushshift_request(submissions_endpoint, params)



def get_pushshift_comments(params: dict):
    # not used, but an example of how to query for comments rather than submissions
    comments_endpoint = "https://api.pushshift.io/reddit/search/comments/"
    return get_pushshift_request(comments_endpoint, params)



def get_new_results(results):
    """returns the new results from the iterable. If the history flag is not used, the given parameter is returned """

    tobe_processed = []
    if configs.history:
        for result in results:
            try:
                # only add the result if it is new
                if not historyandfailure.submission_is_in_history(result):
                    tobe_processed.append(result)
            except Exception:
                # if we can't process the result to put it in history, it is most likely corrupted, hence do not add it to the list to be processed
                pass
    else:
        tobe_processed = results
    
    configs.my_print("Number of new (not in history) results from pushshift request: " + str(len(tobe_processed)))

    return tobe_processed



def get_and_process_submissions(my_params: dict, nb_wanted_results: int, functions: list):
    """Starts the thread which processes submissions and the also starts getting submissions from the pushshift API"""

    processing_thread = Thread(target = submissionhandler.process_submissions, args = [functions])
    processing_thread.start()
    get_submissions(my_params, nb_wanted_results)



def get_submissions(my_params: dict, nb_wanted_results: int):
    """Recursively gets submissions from the pushshift API until the wanted amount has been reached. If there are no specific wanted amounts, it will continue to get new submissions until no new submission are returned by the pushshift API"""

    # this makes it so the exit strategy does not
    # consider the number of results so far
    if nb_wanted_results == 0:
        # 100 is the maximum size supported by pushshift at
        # the time this program was created
        my_params["size"] = "100"
        nb_wanted_results = None

    bad_return_count = 0

    while 1:
        response, results = get_pushshift_submissions(my_params)
        # This ensures that the program closes if the wifi disconnects, pushshift crashes, etc. We use a different value than max_retries as it is a very different scenario
        if not response or not results:
            bad_return_count += 1
            if bad_return_count > 5:
                configs.my_print("Program ended early due to unexpected errors. Check your wifi connection or use the following link to ensure that the pushshift api server is active: https://api.pushshift.io/reddit/search/submission")
                break
            else:
                continue

        bad_return_count = 0

        nb_results = count_elements_in_iterable(results)
        if nb_results == 0:
            break

        tobe_processed = get_new_results(results)
        nb_new = len(tobe_processed)
        configs.my_print("adding " + str(len(tobe_processed)) + " submissions to be processed")
        configs.all_submissions.extend(tobe_processed)
        configs.total_nb_submissions += nb_new

        if nb_wanted_results:
            nb_wanted_results -= nb_new
            my_params["size"] = [str(min(nb_wanted_results, 100))]
        
        if nb_wanted_results == 0:
            # must check for == 0 explicitly as None (unlimited results) is also false
            # if we have all the results we wanted, it is over
            break

        last_element = get_last_from_iterable(results)
        try:
            creation_date = last_element.get("created_utc")
        except Exception:
            # increment by 5 minutes if we cannot get the creation utc
            creation_date += 300
            
        # If the after flag is used (or both after and before), pushshit api will return results in ascending order of date, hence the last one should be used as the new 'after'. If only the before flag is used, the results will be in descending order of date, hence it is the 'before' parameter which should be updated
        if my_params.get("after"):
            my_params["after"] = [creation_date]
        else:
            my_params["before"] = [creation_date]

    print("Last used parameters:")
    print(my_params)
    configs.done_getting_submissions = True