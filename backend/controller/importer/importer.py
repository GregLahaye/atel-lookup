"""
Contains functions that handles the import of ATel reports as well as the
parsing and extraction of ATel data.

Author:
    Nathan Sutardi

License Terms and Copyright:
    Copyright (C) 2021 Nathan Sutardi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import re

from model.constants import FIXED_KEYWORDS_REGEX
from model.ds.report_types import ImportedReport
#from model.db_helper import report_exists
#from model.db_helper import add_report

from datetime import datetime
from astropy.coordinates import SkyCoord
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError
from pyppeteer.errors import TimeoutError

# Regex for extracting the month of submission date
MONTHS_REGEX = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'

# Custom exceptions
class ReportAlreadyExistsError(Exception):
    pass

class NetworkError(Exception):
    pass

class DownloadFailError(Exception):
    pass

# Public functions
def import_report(atel_num: int):
    """
    Adds new ATel report to the database if it is valid.

    Args:
        atel_num (int): The ATel number of the new report to be added.

    Raises:
        ReportAlreadyExistsError: Thrown when report with the ATel number has been added to the database previously.
        ReportNotFoundException: Thrown when report with the ATel number is not found on the AT website.
    """

    #if(report_exists(atel_num) == True):
        #raise ReportAlreadyExistsError(f'ATel #{atel_num} already exists in the database')
    
    #parse_report(download_report(atel_num))
    pass

def import_all_reports():
    """
    Adds all new ATel reports to the database starting after the last ATel report imported.
    """
    pass

# Private functions
def download_report(atel_num: int) -> str:
    """
    Downloads the HTML of ATel report.

    Args:
        atel_num (int): The ATel number of the report to be downloaded.

    Returns:
        str: String representation of the downloaded HTML.

    Raises:
        NetworkError: Thrown when network failure occurs during the HTML download.
        DownloadFailError: Thrown when the HTML could not be downloaded.
    """

    try:
        # Generates the URL of ATel page
        url = f'https://www.astronomerstelegram.org/?read={atel_num}'

        # Makes a GET request to ATel page
        session = HTMLSession()
        request = session.get(url)

        # Fully loads the HTML of ATel page
        request.html.render(timeout=20)
        html = request.html.raw_html

        return html
    except ConnectionError as err:
        raise NetworkError(f'Network failure encountered: {str(err)}')
    except HTTPError as err:
        raise NetworkError(f'Network failure encountered: {str(err)}')
    except TimeoutError as err:
        raise DownloadFailError(f'Couldn\'t download HTML: {str(err)}')
    finally:
        # Closes connection
        session.close()

def parse_report(atel_num: int, html_string: str) -> ImportedReport:
    """
    Extracts data from ATel report as stated in non-functional requirement 1 in the SRS.

    Args:
        atel_num (int): The ATel number of the report to be parsed.
        html_string (str): String representation of the downloaded HTML of ATel report from which to extract data from.

    Returns:
        ImportedReport: Object containing all extracted data from the ATel report.

    Raises:
        MissingReportElementException: Thrown when important data could not be extracted or are missing from the report.
    """

    # Parses HTML into a tree
    soup = BeautifulSoup(html_string, 'html.parser')

    # Extracts title and authors of ATel report
    title = soup.find('h1', {'class': 'title'}).get_text(strip=True)
    authors = soup.find('strong').get_text(strip=True)
    body = ''

    # Finds all possible paragraphs in the HTML
    texts = soup.find_all('p', {'class': None, 'align': None})

    # Filters out non body text elements and formats the body text
    for text in texts:
        if((text.find('iframe') == None) and (len(text.get_text(strip=True)) != 0) and ('Referred to by ATel #:' not in text.get_text(strip=True))):
            if('\n' in text.get_text()):
                body += text.get_text()
            else:
                body += text.get_text() + '\n'

    # Extracts submission date of ATel report
    elements = soup.find_all('strong')
    submission_date = elements[1].get_text(strip=True)

    # Extracts submission date elements
    datetime_values = re.findall('\d+', submission_date)
    month = re.search(MONTHS_REGEX, submission_date).group()

    month_number = 0

    # Assigns appropriate month number based on the month name
    if(month == 'Jan'):
        month_number = 1
    elif(month == 'Feb'):
        month_number = 2
    elif(month == 'Mar'):
        month_number = 3
    elif(month == 'Apr'):
        month_number = 4
    elif(month == 'May'):
        month_number = 5
    elif(month == 'Jun'):
        month_number = 6
    elif(month == 'Jul'):
        month_number = 7
    elif(month == 'Aug'):
        month_number = 8
    elif(month == 'Sep'):
        month_number = 9
    elif(month == 'Oct'):
        month_number = 10
    elif(month == 'Nov'):
        month_number = 11
    elif(month == 'Dec'):
        month_number = 12

    # Submission date is bundled into datetime object
    formatted_submission_date = datetime(year=int(datetime_values[1]), month=month_number, day=int(datetime_values[0]), hour=int(datetime_values[2]), minute=int(datetime_values[3]))

    return ImportedReport(atel_num, title, authors, body.strip(), formatted_submission_date, [], [], extract_keywords(body.strip()), [], [], [])

def extract_coords(body_text: str) -> list[str]:
    """
    Finds all coordinates in the body text of ATel report.

    Args:
        body_text (str): Body text of ATel report.

    Returns:
        list[str]: List of coordinates found.
    """
    return []

def parse_coords(coords: list[str]) -> list[SkyCoord]:
    """
    Parse coordinates that were found into appropriate format so that they can be used to query SIMBAD.

    Args:
        coords (list[str]): List of coordinates found in the body text of ATel report.

    Returns:
        list[SkyCoord]: List of formatted coordinates.
    """
    return []

def extract_dates(body_text: str) -> list[str]:
    """
    Finds all dates in the body text of ATel report.

    Args:
        body_text (str): Body text of ATel report.

    Returns:
        list[str]: List of dates found.
    """
    return []

def parse_dates(dates: list[str]) -> list[datetime]:
    """
    Parse dates that were found into datetime objects so that they can be inserted easily to the database.

    Args:
        dates (list[str]): List of dates found in the body text of ATel report.

    Returns:
        list[datetime]: List of datetime objects representing dates.
    """
    return []

def extract_known_aliases(body_text: str) -> list[str]:
    """
    Finds all known aliases in the body text of ATel report.

    Args:
        body_text (str): Body text of ATel report.

    Returns:
        list[str]: List of known aliases found.
    """
    return []

def extract_keywords(body_text: str) -> list[str]:
    """
    Finds all keywords in the body text of ATel report.

    Args:
        body_text (str): Body text of ATel report.

    Returns:
        list[str]: List of keywords found.
    """

    regex = ''

    # Regex to match all keywords
    for keyword in FIXED_KEYWORDS_REGEX:
        regex = f'{regex}{keyword}|'

    # Removes the last OR operator from regex
    regex = regex.rstrip(regex[-1])

    # Finds all keywords in the body text using regex
    keywords_regex = re.compile(regex)
    keywords = keywords_regex.findall(body_text.lower())

    return list(dict.fromkeys(keywords))