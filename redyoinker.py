import configs, historyandfailure, operationhandler, pushshiftscrapper, os
from sys import exit
from signal import signal, SIGINT
from argumentparser import parse_arguments


def signal_handler(sig, frame):
    """Gracefully quits the program when the Ctrl+C input is detected rather than crash because of an exception (default python behavior)"""
    print('You pressed Ctrl+C!')
    os._exit(0)



def main():

    signal(SIGINT, signal_handler)
    my_params, options = parse_arguments()
    
    subreddits = my_params.get("subreddit")
    if options["subcommand"] == "history":
        if options["show_history"]:
            historyandfailure.show_history(subreddits)
        elif options["clear_history"]:
            historyandfailure.clear_history(subreddits)
        elif options["show_fails"]:
            historyandfailure.show_failures(subreddits)
        elif options["clear_fails"]:
            historyandfailure.clear_failures(subreddits)
    else:
        functions = []
        if configs.history:
            historyandfailure.initialize_history(subreddits)
        if options["retry_fails"]:
            historyandfailure.retry_failures(subreddits)
            exit(0)
        if options["show_json"]:
            functions.append(operationhandler.show_json)
        if options["show_title"]:
            functions.append(operationhandler.show_title)
        if options["show_flink"]:
            functions.append(operationhandler.show_full_link)
        if options["show_media_url"]:
            functions.append(operationhandler.show_media_url)
        if options["download"]:
            functions.append(operationhandler.download_submission_media)

        pushshiftscrapper.get_and_process_submissions(my_params, configs.size, functions)

if __name__ == "__main__":
    main()