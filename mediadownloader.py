import os, configs
from ratelimit import limits, sleep_and_retry
from requests import get
from zipfile import ZipFile
from typing import List
from time import sleep
from re import sub
from unicodedata import normalize


download_folder: str = None


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = normalize('NFKC', value)
    else:
        value = normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = sub(r'[^\w\s-]', '', value.lower())
    return sub(r'[-\s]+', '-', value).strip('-_')



def get_safe_title(unsafe_title: str):
    title = slugify(unsafe_title)
    title = title[:100] + " (title truncated)" if len(title) > 100 else title
    return title



def download_from_url(url: str, title: str) -> bool:
    
    if "i.redd.it" in url:
        return download_from_reddit(url, title)
    elif "reddit" in url:
        # it is not an image so we do not download it. There are no errors so still return True
        return True
    elif "imgur" in url:
        return download_from_imgur(url, title)
    else:
        return download_from_unknown(url, title)



def get_img(my_url: str):
    response = None
    for i in range (0, configs.maxrepeat):
        try:
            response = get(url=my_url)
            if response.status_code == 200:
                break
            else:
                # if it simply does not exist anymore, no need to try again
                if response.status_code == 404:
                    break
                # too many requests are dangerous because the server may ban us if it happens often. As such, sleep for minimum 3s
                elif response.status_code == 429:
                    sleep_time = float(response.headers.get('Retry-After', configs.timeout))
                    sleep_time = min(sleep_time, 3)
                    sleep(sleep_time)
                else:
                    sleep_time = float(response.headers.get('Retry-After', configs.timeout))
                    sleep(sleep_time)
        except Exception:
            pass

    is_valid = response and response.status_code == 200

    if is_valid:
        content = response.headers.get("Content-Type")
        if "text" not in content and "html" not in content:
            return response
        else:
            return None
    else:
        return None



def find_unique_name(safe_title: str, ext: str) -> str:
    file_name = safe_title + "." + ext
    i = 1
    while os.path.exists(os.path.join(download_folder, file_name)):
        file_name = safe_title + str(i) + "." + ext
        i += 1
    return os.path.join(download_folder, file_name)



@sleep_and_retry
@limits(calls=configs.dic_request_limit["reddit"], period=60)
def get_img_reddit(url: str):
    return get_img(url)



@sleep_and_retry
@limits(calls=configs.dic_request_limit["imgur"], period=60)
def get_img_imgur(url: str):
    return get_img(url)



@sleep_and_retry
@limits(calls=configs.dic_request_limit["any"], period=60)
def get_img_imgur(url: str):
    return get_img(url)



def download_from_reddit(reddit_url: str, title: str) -> bool:
    response = None
    response = get_img_reddit(reddit_url) 

    if response:
        # all reddit urls have the file extension at the end
        ext = reddit_url.split(".")[-1]
        safe = get_safe_title(title)
        file_name = find_unique_name(safe, ext)
        with open(file_name, "wb") as f:
            f.write(response.content)
            return True
    else:
        return False



def download_from_unknown(my_url: str, title: str) -> bool:
    response = None
    response = get_img(my_url)

    if not response:
        return False

    content_type = response.headers.get("Content-Type")
    if content_type:
        ext = content_type.split("/")[-1]
        if "jpeg" in ext:
            ext = "jpg"
        if response:
            file_name = find_unique_name(get_safe_title(title), ext)
            with open(file_name, "wb") as f:
                f.write(response.content)
                return True
    else:
        # if there is no content-type, we cannot download, because we don't even know what to save
        return False



def download_from_imgur(imgur_url: str, title: str) -> bool:
    response = None
    is_album = "/a/" in imgur_url
    no_extension = len(imgur_url) - imgur_url.rindex(".") > 4

    if "/gallery/" in imgur_url:
        imgur_url = imgur_url.replace("/gallery/", "/") + ".png"

    if is_album:
        imgur_url = imgur_url + "/zip"
    elif no_extension:
        imgur_url += ".png" 

    if ".gifv" in imgur_url:
        # get the video file instead of the gifv
        # optionally use the .gif url to get the gif file
        imgur_url = imgur_url.split(".gifv")[0] + ".mp4"
        
    response = get_img_imgur(imgur_url) 

    if not response:
        return False
    # when the content length for imgur is 503 it means that the image has been deleted
    if len(response.content) == 503:
        return False

    # for imgur, we assume that it is a jpg. This allows us to perhaps download an image even when the extension is not indicated (very rare)
    ext = "jpg"
    content_type = response.headers.get("Content-Type")
    if content_type:
        ext = content_type.split("/")[-1]
    if "x-zip" in ext:
        ext = "zip"
    elif "jpeg" in ext:
        ext = "jpg"

    full_name = find_unique_name(get_safe_title(title), ext)
    with open(full_name, 'wb') as f:
        f.write(response.content)
        if is_album:
            new_names = []
            if "zip" in ext:
                try:
                    with ZipFile(full_name) as file:
                        names = file.namelist()
                        for f in names:
                            new_names.append(os.path.basename(file.extract(f, download_folder)))
                except Exception:
                    try:
                        os.remove(full_name)
                    except OSError:
                        pass      
                    return False

                os.remove(full_name)
                rename_album_images(title, new_names)
        return True



def rename_album_images(title: str, names: List[str]):
    title = title.split(".")[0]
    for i in range(0, len(names)):
        f = names[i]
        ext = f.split(".")[-1]
        file_name = find_unique_name(title, ext)
        os.rename(os.path.join(download_folder, f), file_name)