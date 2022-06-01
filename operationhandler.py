import mediadownloader
from pprint import pprint
from typing import List



def show_title(submission: dict):
    print(submission.get("title"))
    return True



def show_full_link(submission: dict):
    print(submission.get("full_link"))
    return True



def show_media_url(submission: dict):
    urls = get_media_url(submission)
    for url in urls:
        print(url)
    return True
    


def show_json(submission: dict):
    pprint.pprint(submission)
    return True



def download_submission_media(submission: dict):
    """Downloads the content of media urls from a submission (reddit post) dictionary"""

    failed = False
    urls = get_media_url(submission)
    for url in urls:
        if not mediadownloader.download_from_url(url, submission.get("title")):
            failed = True
    
    return not failed
            


def get_media_url(submission: dict) -> List[str]:
    """Gets the media urls from a submission (reddit post) dictionary"""
    urls = []
    if hasattr(submission, "is_gallery"):
        meta = get_urls_from_meta(submission.get("media_metadata"), submission.gallery_data['items'])
        urls.append(meta)
    elif submission.get("domain") == "gfycat.com":
        urls.append(submission.get("preview").get("images")[0].get("source").get("url").split("?")[0])
    elif submission.get("domain") == "redgifs.com":
        url = str(submission.get("media").get("oembed").get("thumbnail_url"))
        url = url[:url.rfind(".")] + ".mp4"
        urls.append(url)
    elif not submission.get("is_self"):
        urls.append(submission.get("url"))

    return urls



def get_urls_from_meta(media_metadata, gallery_data_items) ->  List[str]:
    """Get the media urls from reddit galleries"""

    i = 1
    ids = [i['media_id'] for i in gallery_data_items]
    urls = []
    for id in ids:
        url = media_metadata[id]['p'][0]['u']
        url = url.split("?")[0].replace("preview", "i")
        urls.append(url)
    return urls
    