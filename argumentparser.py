from typing import Dict, List, Tuple, Union
import argparse, os, configs, mediadownloader
from datetime import datetime



def integer_format_validator_helper(temp: str, msg: str) -> int:
    try:
        someVal = int(temp)
        if someVal < 0:
            raise argparse.ArgumentTypeError(msg)
        else:
            return someVal
    except:
        raise argparse.ArgumentTypeError(msg)



def integer_format_validator(temp: str) -> int:
    msg = "Must be a positive integer"
    return integer_format_validator_helper(temp, msg)



def size_format_validator(temp: str) -> int:
    msg = "Must be a positive integer or 'inf' or 'infinity'"   
    if temp == "inf" or temp == "infinity":
        return int(0)
    else:
        return integer_format_validator_helper(temp, msg)
        


def date_format_validator(temp: str) -> str:
    msg = "Invalid format"
    try:
        epoch = int(datetime.fromisoformat(temp).timestamp())
        return str(epoch)
    except:
        raise argparse.ArgumentTypeError(msg)



def folder_format_validator(temp: str) -> str:
    if os.path.isdir(temp):
        return temp
    else:
        raise argparse.ArgumentTypeError("Not a folder")



def setPushshiftParams(my_params: Dict[str, Union[List[str], str]], args: argparse.Namespace):
    my_params["size"] = args.size

    before = args.before
    after = args.after
    minscore = args.minscore
    maxscore = args.maxscore

    if minscore or maxscore:
        if minscore:
            my_params["score"] = ">"+str(minscore)
        if maxscore:
            my_params["score"] = "<"+str(maxscore)

    if before:
        my_params["before"] = [before]
    else:
        my_params["before"] = str(int(datetime.now().timestamp()))

    if after:
        my_params["after"] = [after]



def parse_arguments() -> Tuple[Dict[str, Union[List[str], str]], Dict[str, any]]:
    parser = argparse.ArgumentParser(description="This app is a subreddit scrapper for images and videos. It also has a history feature which prevents you from downloading/processing the same submission twice (does not consider crossposting) and allows you to retry unsuccessful downloads if needed.")
    subparsers = parser.add_subparsers(help='help for subcommand', dest="subcommand")

    scrap_parser = subparsers.add_parser('scrap', help='scrap help')
    history_parser = subparsers.add_parser('history', help='history help')

    scrap_parser.add_argument("-t", "--timeout", type=integer_format_validator, default=2, help="Timeout: How long to wait, in seconds, after a request fails (default 2).")

    scrap_parser.add_argument("-r", "--maxrepeat", type=integer_format_validator, default=3, help="Max retries: The maximum number of times to retry a request before giving up (default 3).")

    scrap_parser.add_argument("-sm", "--minscore", type=integer_format_validator, default=None, help="Score: the minimum amount of point that a post needs to be included (default 1).")

    scrap_parser.add_argument("-sx", "--maxscore", type=integer_format_validator, default=None, help="Score: the maximum amount of point that a post can have to be included (default infinity).")

    scrap_parser.add_argument("-s", "--size", type=size_format_validator, default=25, help="Size: The number of results wanted. Use 0/inf/infinity to get as many as are returned (default 25).")

    scrap_parser.add_argument("-b", "--before", type=date_format_validator, default=None, help="Before: The maximum (inclusive) creation date a post can have to be included in ISO 8601 format, i.e. yyyy-mm-dd [hh:mm:ss.mmm]. Hours, minutes and seconds are optional. Milliseconds will be ignored though they can be included.")

    scrap_parser.add_argument("-a", "--after", type=date_format_validator, default=None, help="Before: The maximum (inclusive) creation date a post can have to be included in ISO 8601 format, i.e. yyyy-mm-dd [hh:mm:ss.mmm]. Hours, minutes and seconds are optional. Milliseconds can be included but they will be ignored.")

    scrap_parser.add_argument("-ti", "--title", action="store_true", help="Use this flag to display the posts titles")

    scrap_parser.add_argument("-u", "--murl", action="store_true", help="Use this flag to display the posts' media urls (urls to directly access the images/videos in the post)")

    scrap_parser.add_argument("-fl", "--flink", action="store_true", help="Use this flag to display the posts full links")

    scrap_parser.add_argument("-js", "--json", action="store_true", help="Use this flag to display the json of submission")

    scrap_parser.add_argument("-ht", "--history", action="store_true", help="Use this flag to save the results in history and exclude those who are already in history")

    scrap_parser.add_argument("-rfail", "--retryfails", action="store_true", help="Use this flag to try to download again using the failed download history. No other action will be taken. Use the other flags as usual for download directory, timeout, etc. If no download directory is given, the directory of this script will be used. Use the empty string with the subreddit flag to retry for all eligible subreddits (subreddits shown with the --showfail flag).")

    scrap_parser.add_argument("-d", "--download", type=folder_format_validator, help="The folder where to download files. If not used (or empty string), media will not be downloaded.")

    history_group = history_parser.add_mutually_exclusive_group(required=True)

    history_group.add_argument("-cht", "--clearhist", action="store_true", help="Use this flag to clear the history. No other action will be taken. Only the subreddits flag will be considered with this flag. Use the empty string with the subreddit flag to delete the entire history")

    history_group.add_argument("-sht", "--showhist", action="store_true", help="Use this flag to show the history and its save location on your machine. No other action will be taken regardless of the other flags used.")

    history_group.add_argument("-cfail", "--clearfails", action="store_true", help="Use this flag to clear the failed download history. No other action will be taken. Only the subreddits flag will be considered with this flag. Use the empty string with the subreddit flag to delete the failed download history of all subreddits")

    history_group.add_argument("-sfail", "--showfails", action="store_true", help="Use this flag to show the number of failed downloads for each subreddit and their save location on your machine. If a subreddit does not appear, it means there are no failures associated with it.")

    parser.add_argument("-subs", "--subreddits", help='Subreddits: The name of all subreddits to include in the command, seperated by spaces (e.g. "askreddit pcgamers linux"). Must match exactly the name as it is on reddit for the history to work properly.')

    parser.add_argument("-v", "--verbose", action="store_true", help="Use this flag to display execution logs")


    my_params: Dict[str, Union[List[str], str]] = {}
    options: Dict[str, any] = {}

    args = parser.parse_args()
    configs.display_logs = bool(args.verbose)

    if args.subreddits:
        my_params["subreddit"] = (str(args.subreddits)).split()
    else:
        my_params["subreddit"] = []

    options["subcommand"] = args.subcommand

    if args.subcommand == "scrap":

        # plus 1 because we try at least once
        configs.maxrepeat = args.maxrepeat + 1

        configs.timeout = args.timeout
        configs.size = args.size
        configs.history = bool(args.history)
        options["show_title"] = bool(args.title)
        options["show_media_url"] = bool(args.murl)
        options["show_flink"] = bool(args.flink)
        options["show_json"] = bool(args.json)
        options["retry_fails"] = bool(args.retryfails)
        options["download"] = bool(args.download)

        mediadownloader.download_folder = os.getcwd()
        if options["download"]:
            mediadownloader.download_folder = str(args.download)
        elif options.get("retry_fails"):
            mediadownloader.download_folder = os.getcwd()

        setPushshiftParams(my_params, args)
        return my_params, options

    elif args.subcommand == "history":
        options["show_history"] = bool(args.showhist)
        options["clear_history"] = bool(args.clearhist)
        options["show_fails"] = bool(args.showfails)
        options["clear_fails"] = bool(args.clearfails)
        return my_params, options

    else:
        print("No command selected (scrap | history). Use program -h for the usage")
        exit(1)
    