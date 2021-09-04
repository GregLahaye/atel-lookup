"""
Contains functions that handles the import and download of ATel reports.

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

from model.db.db_interface import report_exists, add_report
from controller.importer.parser import parse_report

from requests_html import HTMLSession
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError
from pyppeteer.errors import TimeoutError

# Custom exceptions
class ReportAlreadyExistsError(Exception):
    pass

class ReportNotFoundError(Exception):
    pass

class NetworkError(Exception):
    pass

class DownloadFailError(Exception):
    pass

# Importer functions
def import_report(atel_num: int):
    """
    Adds new ATel report to the database if it is valid.

    Args:
        atel_num (int): The ATel number of the new report to be added.

    Raises:
        ReportAlreadyExistsError: Thrown when report with the ATel number has been added to the database previously.
        ReportNotFoundError: Thrown when report with the ATel number is not found on the AT website.
    """

    # Raises error when ATel report is already imported into the database
    if(report_exists(atel_num) == True):
        raise ReportAlreadyExistsError(f'ATel #{atel_num} already exists in the database')
    
    html_string = download_report(atel_num)

    # Raises error when ATel report is not found
    if(html_string is None):
        raise ReportNotFoundError(f'ATel #{atel_num} does not exists')

    # Parses HTML and imports ATel report into the database
    add_report(parse_report(atel_num, html_string))

def import_all_reports():
    """
    Adds all new ATel reports to the database starting after the last ATel report imported.
    """
    pass

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

    session = None

    try:
        # Generates the URL of ATel page
        url = f'https://www.astronomerstelegram.org/?read={atel_num}'

        # Makes a GET request to ATel page
        session = HTMLSession()
        request = session.get(url)

        # Fully loads the HTML of ATel page
        request.html.render(timeout=20)
        html = request.html.raw_html

        # Determines whether ATel report exists
        soup = BeautifulSoup(html, 'html.parser')
        texts = soup.find_all('p', {'class': None, 'align': None})

        if(texts[1].get_text(strip=True) == 'This ATel does not appear to exist.'):
            html = None

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