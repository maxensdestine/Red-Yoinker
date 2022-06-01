import configs, historyandfailure
from time import sleep
from copy import deepcopy



def process_submissions(functions: list):
    """Process submissions as they are obtained from the pushshift API"""
    configs.my_print("submission processor started")
    while configs.all_submissions or not configs.done_getting_submissions:
        submissions = deepcopy(configs.all_submissions)
        if submissions:
            for submission in submissions:
                already_added = False
                for function in functions:
                    try:
                        if not function(submission) and not already_added:
                            historyandfailure.add_to_failure(submission)
                            already_added = True
                    except Exception as e:
                        if not already_added:
                            historyandfailure.add_to_failure(submission)
                            already_added = True

                # if already_added is false, all functions were successful
                if configs.history and not already_added:
                    historyandfailure.add_to_history(submission)


                configs.nb_of_processed_submissions += 1
                configs.my_print("Processed " + str(configs.nb_of_processed_submissions) + "/" + str(configs.total_nb_submissions)+ "\r")
                
            del configs.all_submissions[:len(submissions)]
        else:
            configs.my_print("No submission waiting for processing")
            sleep(1)