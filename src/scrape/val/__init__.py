from enum import Enum
import sys
from rich import print
from urllib.parse import urlparse
import requests
from seleniumwire import webdriver
from selenium import webdriver as swd
from datetime import timedelta, datetime
import re
from typing import List
import base64
import magic


def window(lst: List[int], size: int, stride: int) -> List[List[int]]:
    """
    Creates a sliding window over a list.

    Args:
        lst (List[int]): The input list.
        size (int): The size of the window.
        stride (int): The stride between windows.

    Returns:
        List[List[int]]: A list of sublists created by sliding the window over the input list.
    Raises:
        ValueError: If the window size or stride is less than or equal to zero, or if the window size exceeds the list length.
    """
    if size <= 0 or stride <= 0:
        raise ValueError("Window size and stride must be greater than zero.")
    if size > len(lst):
        raise ValueError("Window size cannot exceed the list length.")

    return [lst[i : i + size] for i in range(0, len(lst), stride)]


def printinfo(s: str):
    """
    Prints an information message to stderr.

    Args:
        s (str): The message to be printed.
    """
    print("[bold blue]Info:", s, file=sys.stderr)


def printerr(s: str):
    """
    Prints an error message to stderr.

    Args:
        s (str): The error message to be printed.
    """
    print("[red]:x: Error:", s, file=sys.stderr)


def printwarn(s: str):
    """
    Prints a warning message to stderr.

    Args:
        s (str): The warning message to be printed.
    """
    print("[bold yellow]:warning: Warning:", s, file=sys.stderr)


def get_webdriver(conf):
    """
    Retrieves the appropriate web driver based on the configuration.

    Args:
        conf: The configuration object.

    Returns:
        WebDriver: An instance of the web driver.
    """
    options = {
        "proxy": {
            "http": conf.http_proxy,
            "no_proxy": "localhost,127.0.0.1",
        }
    }
    if conf.http_proxy is not None:
        return webdriver.Chrome(seleniumwire_options=options)
    else:
        return swd.Chrome()


def escape_unsafe_characters(filename: str) -> str:
    """
    Escapes unsafe characters in a filename.

    Args:
        filename (str): The filename to be escaped.

    Returns:
        str: The escaped filename.
    """
    unsafe_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'
    return re.sub(unsafe_chars, "_", filename)


def handle_media_url(url: str, file_name: str, raw_file_name: bool, conf):
    """
    Handles a media URL based on the configuration options.

    Args:
        url (str): The URL of the media.
        file_name (str): The desired file name.
        raw_file_name (bool): Flag indicating whether to use the raw file name.
        conf: The configuration object.

    Returns:
        str: The original URL or data URL.
    """
    if conf.download_media or conf.embed_media:
        data = download(url, conf)
        if data is None:
            printerr(f"Saving '{url}' to '{file_name}' failed")
            return url
        if conf.download_media:
            if raw_file_name:
                save_raw(url, data, file_name)
            else:
                save(url, file_name, data)
        if conf.embed_media:
            return to_data_url(data)
    return url


def to_data_url(file_data):
    """
    Converts file data to a data URL.

    Args:
        file_data: The data of the file.

    Returns:
        str: The data URL.
    """
    base64_data = base64.b64encode(file_data).decode("utf-8")

    mime_type = magic.from_buffer(file_data, mime=True)
    if mime_type is None:
        mime_type = "application/octet-stream"

    return "data:{};base64,{}".format(mime_type, base64_data)

def escape_key(s: str) -> str:
    return s.replace(" ", "_").lower()

def download(url: str, conf):
    """
    Downloads content from a URL.

    Args:
        url (str): The URL to download from.
        conf: The configuration object.

    Returns:
        bytes: The downloaded content, or None if the download failed.
    """
    proxy = {}
    if conf.http_proxy is not None:
        proxy["http"] = conf.http_proxy

    response = requests.get(url, proxies=proxy)
    if response.status_code == 200:
        return response.content
    else:
        return None


def save_raw(url: str, data, file_name: str):
    """
    Saves data to a file with filename.

    Args:
        url (str): The URL from which the data was retrieved.
        data: The data to be saved.
        file_name (str): The name of the file.
    """
    with open(file_name, "wb") as file:
        file.write(data)
        printinfo(f"Saved '{url}' to '{file_name}'")


def save(url: str, file_name: str, data):
    """
    Saves data to a file with file extension from url.

    Args:
        url (str): The URL from which the data was retrieved.
        file_name (str): The name of the file.
        data: The data to be saved.
    """
    file_ending = urlparse(url).path.split(".")[-1]
    file_name = f"{file_name}.{file_ending}"
    save_raw(url, data, file_name)


def splitat(s: str, p: str) -> (str, str):
    """
    Splits a string at the first occurrence of a separator.

    Args:
        s (str): The string to be split.
        p (str): The separator.

    Returns:
        Tuple[str, str]: A tuple containing the part before the separator and the part after the separator.
    """
    split_values = s.split(p, 1)
    lang, value = p.join(split_values[:-1]), split_values[-1]
    return (lang, value)


def parse_duration(s: str) -> timedelta:
    """
    Parses a duration string into a timedelta object.

    Args:
        s (str): The duration string.

    Returns:
        timedelta: The parsed duration as a timedelta object, or None if the string doesn't match any valid format.
    """
    try:
        # format: "? h ? min"
        hours = int(re.search(r"(\d+)\s*h", s).group(1))
        minutes = int(re.search(r"(\d+)\s*min", s).group(1))
        return timedelta(hours=hours, minutes=minutes)
    except:
        pass

    try:
        # format: "??:??:??"
        hours = int(s.split(":")[0])
        minutes = int(s.split(":")[1])
        seconds = int(s.split(":")[2])
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except:
        pass

    try:
        # format : "??:??:??.??"
        time_duration = datetime.strptime(s, "%H:%M:%S.%f").time()
        return timedelta(
            hours=time_duration.hour,
            minutes=time_duration.minute,
            seconds=time_duration.second,
            microseconds=time_duration.microsecond,
        )
    except:
        pass

    try:
        # format : ??m
        if s.endswith("m"):
            (min_d, _) = s.split("m", 2)
            return timedelta(minutes=float(min_d))
    except:
        pass

    # no valid format found
    return None


def scrollToEnd(b):
    """
    Scrolls to the end of the page
    """
    b.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def scrollToElement(b, e):
    """
    Scrolls to the supplied element
    """
    b.execute_script("arguments[0].scrollIntoView();", e)


def currency(v: str) -> dict:
    """
    Parses a currency value string into a dictionary.

    Args:
        v (str): The currency value string.

    Returns:
        dict: A dictionary containing the currency and value.
    """
    return {"currency": v[-1:], "value": float(v[:-1].replace(",", "."))}


class Language(Enum):
    """
    An enumeration representing supported languages.
    """

    en_US = 1
    de_DE = 2
