"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Halyna Kaida
email: lina.g@ukr.net
"""


import csv
import argparse
import requests
from bs4 import BeautifulSoup


def get_soup(link: str) -> BeautifulSoup:
    """
    The function gets a Beautifulsoup.
    """
    web = requests.get(link)
    return BeautifulSoup(web.text, features="html.parser")


def get_location_link(link: str, location_code: str) -> str:
    """
    The function gets a location URL from entered URL and location code.
    """
    code_tag_a = location_code.find("a")
    location_link = code_tag_a.get("href")
    return "/".join(link.split("/")[:5]) + "/" + location_link


def get_voices(link: str, code: str, location: str) -> dict:
    """
    The function gets all data and 
    voices of each political party for entered location.
    """
    soup = get_soup(link)
    voices = {
              "code": code,
              "location": location,
              "registered": soup.find("td", {"headers": "sa2"}).text, 
              "envelopes": soup.find("td", {"headers": "sa3"}).text, 
              "valid": soup.find("td", {"headers": "sa6"}).text
              }
    parties = soup.find_all("td", {"class": "overflow_name"})
    values = (soup.find_all("td", {"headers": "t1sa2 t1sb3"}) + 
              soup.find_all("td", {"headers": "t2sa2 t2sb3"}))
    parties_voices = dict(zip([party.text for party in parties], 
                       [value.text for value in values]))
    voices.update(parties_voices)   
    return voices


def write_file_csv(file: str, header, results: list):
    """
    The function creates and writes the file with the results. 
    """
    with open(file, mode = "w", encoding="UTF-8") as csv_file:
        writer_file = csv.DictWriter(
                                     csv_file, 
                                     fieldnames=header, 
                                     delimiter=";", 
                                     dialect="excel-tab", 
                                     lineterminator="\r"
                                     )
        writer_file.writeheader()
        for res in results:
            writer_file.writerow(res)


def create_result_list(soup: BeautifulSoup) -> list: 
    """
    This function creates the list with results of voices 
    """
    regions = soup.find_all("tr")
    results = []
    for reg in regions:
        loc_code = reg.find("td", {"class": "cislo"})
        location = reg.find("td", {"class": "overflow_name"})
        if loc_code and location:
            location_code = loc_code
            code = location_code.text
            location = location.text
            location_link = get_location_link(link, location_code)
            results.append(get_voices(location_link, code, location))
    return results


def get_args() -> argparse.Namespace:
    """
    This function gets arguments:
    1. URL: for example: 
    'https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ&xkraj=1&xnumnuts=1100'
    (don't forget quotation marks).
    2. CSV filename. For example: results_praha.csv. 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="link", help="Argument that requires 'link'")
    parser.add_argument(dest="file", help="Argument that requires 'file_csv'."
                                        "(For example: results_region.csv)")
    args = parser.parse_args()
    return args


def check_filename(file: str) -> str:
    """
    This function returns filename if it is correct or 
    raises an error if it is not.
    """
    if file.startswith("results_") and file.endswith(".csv"):
        return file
    else:
        print("Incorrect format of the file. Your file should be "
              "in the following format: 'results_region.csv'")
        quit()


def check_link(link: str) -> str:
    """
    This function returns URL if it is correct or 
    raises an error if it is not. 
    """
    if link.startswith('https://www.volby.cz/pls/ps2017nss/ps32'):
        return link
    else:
        print("Incorrect URL. Your link should start with: " \
              "https://www.volby.cz/pls/ps2017nss/ps32")
        quit()


def request_is_ok(link: str) -> bool:
    """
    This function returns True if statuscode is equel '200'.
    """
    r = requests.get(link)
    if r.status_code == 200:
        return True
    

if __name__ == "__main__": 
    link_arg = get_args().link
    file_arg = get_args().file
    link = check_link(link_arg)
    file = check_filename(file_arg)
    try:
        if request_is_ok(link):
            soup = get_soup(link)
            results = create_result_list(soup)
            header = tuple(results[0].keys())
            write_file_csv(file, header, results)
        else:
            print("Requested website responded with error message. " \
                "Please check provided URL and your internet connection.")
            quit()
    except IndexError:
        print("Something is wrong with your URL. Please check if it is correct.")
        quit()
