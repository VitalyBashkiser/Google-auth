import time
import re
from datetime import datetime

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
    Extracts essential information from the contact details with flexible parsing.

    Args:
        contact_text (str): Raw contact text containing address, phone, and fax information.

    Returns:
        str: Cleaned and formatted contact information.
    """
    location_patterns = [
        r'Місцезнаходження.*?[:\s]*([\s\S]*?)(?=E-mail|Дата оновлення|Повні|Пройдіть|\Z)',
        r'Адреса.*?[:\s]*([\s\S]*?)(?=\bТелефон|\bФакс|\n|$)',
        contact_text,
        re.IGNORECASE
    ]

    phone_patterns = [
        r'Телефон[:\s]*([\d\-+() ]+)',
    ]

    fax_patterns = [
        r'Факс[:\s]*([\d\-+() ]+)',
    ]

    def search_patterns(text, patterns):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    location = search_patterns(contact_text, location_patterns)
    phone = search_patterns(contact_text, phone_patterns)
    fax = search_patterns(contact_text, fax_patterns)

    contact_data = [
        f"Address: {clean_text(location)}" if location else None,
        f"Phone: {', '.join(set(phone))}" if phone else None,
        f"Fax: {fax}" if fax else None
    ]

    return " ".join(filter(None, contact_data))


def extract_company_profile(profile_text: str) -> str:
    """
    Extracts a concise company profile, capturing only relevant introductory information.
    """
    match = re.search(r'Юридична особа .*?[\d\.]{10}', profile_text)
    if match:
        profile = match.group(0)
    else:
        profile = profile_text.split("Організаційно-правова форма")[0]
    return clean_text(profile)


def extract_last_inspection_date(parser) -> str:
    """
    Extracts the date of the last inspection or registration from the tax records.

    Args:
        parser (HTMLParser): Parsed HTML content.

    Returns:
        str: Cleaned date text for last inspection.
    """
    dates = []
    for label, value in zip(
        parser.css("div.seo-table-col-2 span.text-grey"),
        parser.css("div.seo-table-col-2 p")
    ):
        if "Дата взяття на облік" in label.text():
            date_text = re.search(r'\d{2}\.\d{2}\.\d{4}', value.text())
            if date_text:
                dates.append(date_text.group(0))

    return clean_text(" | ".join(dates))


def extract_tax_info(parser) -> str:
    """
    Extracts tax-related information, specifically regarding tax cancellation.

    Args:
        parser (HTMLParser): Parsed HTML content.

    Returns:
        str: Cleaned tax information text.
    """
    tax_texts = [
        el.text() for el in parser.css("div.seo-table-row p.seo-table-text")
        if el.text() and re.search(r'анулювання', el.text(), re.IGNORECASE)
    ]
    return clean_text(" ".join(tax_texts))


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
        "code": clean_text(parser.css_first("h2.company-title-code").text()) if parser.css_first(
            "h2.company-title-code") else company_code,
        "status": clean_text(parser.css_first("div.seo-table-row span.text-green").text()) if parser.css_first(
            "div.seo-table-row span.text-green") else None,
        "registration_date": clean_text(
            parser.css_first("div.seo-table-row:nth-child(6) div.seo-table-col-2").text()) if parser.css_first(
            "div.seo-table-row:nth-child(6) div.seo-table-col-2") else None,
        "authorized_capital": clean_text(
            parser.css_first("div.seo-table-row:nth-child(4) div.seo-table-col-2").text()) if parser.css_first(
            "div.seo-table-row:nth-child(4) div.seo-table-col-2") else None,
        "legal_form": clean_text(parser.css_first("p.ucfirst.copy-file-field").text()) if parser.css_first(
            "p.ucfirst.copy-file-field") else None,
        "main_activity": extract_main_activities(" ".join(
            [clean_text(el.text()) for el in parser.css("div.flex-activity span, ul.activities-list li") if
             el.text()])) if parser.css("div.flex-activity span, ul.activities-list li") else None,
        "contact_info": extract_contact_info(" ".join([clean_text(el.text()) for el in parser.css("table.seo-table-item-lg tbody tr td") if el.text()])) if parser.css("table.seo-table-item-lg tbody tr td") else None,
        "authorized_person": " ".join(
            [clean_text(el.text()) for el in parser.css("ul.seo-table-list li") if el.text()]) if parser.css(
            "ul.seo-table-list li") else None,
        "tax_info": extract_tax_info(parser),
        "registration_authorities": " | ".join(
            [clean_text(el.text()) for el in parser.css("div.info-group p") if el.text()]),
        "last_inspection_date": extract_last_inspection_date(parser),
        "company_profile": clean_text(parser.css_first("div.seo-table-generated-text").text()) if parser.css_first(
            "div.seo-table-generated-text") else None,
        "last_updated": datetime.utcnow(),
    }

    return data

