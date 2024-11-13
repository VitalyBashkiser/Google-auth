import time
import re

import requests
from selectolax.parser import HTMLParser

from src.exceptions.errors import PageNotFoundError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1"
}


def clean_text(text: str) -> str:
    """
    Removes extra spaces, line breaks, and unnecessary words from the text.

    Args:
        text (str): Text to clean.

    Returns:
        str: Cleaned text.
    """
    if not text:
        return None
    text = text.replace("копіювати", "").replace("скопійовано", "")
    return " ".join(text.split())


def extract_main_activities(activity_text: str) -> str:
    """
    Extracts the main information from the company's activities.

    Args:
        activity_text (str): Raw activity text containing multiple activities.

    Returns:
        str: Cleaned text with extracted main activities.
    """
    activities = re.findall(r'\d{2}\.\d{2} .*?(?=\d{2}\.\d{2}|\Z)', activity_text)
    return " ".join([clean_text(activity) for activity in activities])


def extract_contact_info(contact_text: str) -> str:
    """
    Extracts essential information from the contact details.

    Args:
        contact_text (str): Raw contact text containing address, phone, and fax information.

    Returns:
        str: Cleaned and formatted contact information.
    """
    location = re.search(r'Місцезнаходження.*?:(.*?) Телефон', contact_text)
    phone = re.search(r'Телефон:\s*([\d\-]+)', contact_text)
    fax = re.search(r'Факс:\s*([\d\-]+)', contact_text)

    contact_data = [
        f"Address: {clean_text(location.group(1))}" if location else None,
        f"Phone: {phone.group(1)}" if phone else None,
        f"Fax: {fax.group(1)}" if fax else None
    ]

    return " ".join(filter(None, contact_data))


def parse_company(company_code: str) -> dict:
    """
    Parses basic company data from a webpage using the company code.

    Args:
        company_code (str): The company code to retrieve information.

    Returns:
        dict: A dictionary containing basic company fields.
    """
    url = f"https://youcontrol.com.ua/catalog/company_details/{company_code}/"
    time.sleep(2)

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    if response.status_code != 200:
        raise PageNotFoundError(url)

    parser = HTMLParser(response.text)

    data = {
        "name": clean_text(parser.css_first("h1.company-name").text()) if parser.css_first("h1.company-name") else None,
        "code": clean_text(parser.css_first("h2.company-title-code").text()) if parser.css_first("h2.company-title-code") else company_code,
        "status": clean_text(parser.css_first("div.seo-table-row span.text-green").text()) if parser.css_first("div.seo-table-row span.text-green") else None,
        "registration_date": clean_text(parser.css_first("div.seo-table-row:nth-child(6) div.seo-table-col-2").text()) if parser.css_first("div.seo-table-row:nth-child(6) div.seo-table-col-2") else None,
        "authorized_capital": clean_text(parser.css_first("div.seo-table-row:nth-child(4) div.seo-table-col-2").text()) if parser.css_first("div.seo-table-row:nth-child(4) div.seo-table-col-2") else None,
        "legal_form": clean_text(parser.css_first("div.seo-table-row:nth-child(5) div.seo-table-col-2").text()) if parser.css_first("div.seo-table-row:nth-child(5) div.seo-table-col-2") else None,
        "main_activity": extract_main_activities(" ".join([clean_text(el.text()) for el in parser.css("ul.activities-list li")])) if parser.css("ul.activities-list li") else None,
        "contact_info": extract_contact_info(" ".join([clean_text(el.text()) for el in parser.css("table.seo-table-item tbody tr")])),
        "authorized_person": " ".join([clean_text(el.text()) for el in parser.css("ul.seo-table-list li")]) if parser.css("ul.seo-table-list li") else None
    }

    return data
