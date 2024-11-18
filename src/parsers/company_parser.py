import time
import re
from datetime import datetime
from loguru import logger

import requests
from selectolax.parser import HTMLParser


from src.exceptions.errors import PageNotFoundError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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
    tax_info_block = parser.css("div.seo-table-row")

    if not tax_info_block:
        return {}

    tax_info = {}
    for row in tax_info_block:
        key_element = row.css_first("div.seo-table-col-1")
        value_element = row.css_first("div.seo-table-col-2")

        if key_element and value_element:
            key = clean_text(key_element.text())
            value = clean_text(value_element.text())

            if key and value:
                tax_info[key] = value

    return "; ".join(tax_info)


def clean_registration_authorities(raw_text: str) -> str:
    """
    Cleans the registration authorities text by removing unwanted symbols and formatting it properly.
    """
    if not raw_text:
        return None
    return raw_text.replace("\n", "").replace(" / ", "; ").strip()


def parse_company(company_code: str, source: str = "youcontrol") -> dict:
    """
    Parses basic company data from a webpage using the company code.

    Args:
        company_code (str): The company code to retrieve information.

    Returns:
        dict: A dictionary containing basic company fields.
    """
    if source == "youcontrol":
        url = f"https://youcontrol.com.ua/catalog/company_details/{company_code}/"
    elif source == "clarity":
        url = f"https://clarity-project.info/edr/{company_code}/"
    else:
        raise ValueError(f"Unsupported source: {source}")
    logger.info(f"Fetching company data from URL: {url}")
    time.sleep(3)

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    if response.status_code != 200:
        raise PageNotFoundError(url)

    parser = HTMLParser(response.text)

    if source == "youcontrol":
        data = {
            "name": clean_text(parser.css_first("h1.company-name").text()) if parser.css_first("h1.company-name") else None,
            "code": company_code,
            "status": clean_text(parser.css_first("span.copy-file-field.status-green-seo").text()) if parser.css_first("span.copy-file-field.status-green-seo") else None,
            "registration_date": clean_text(parser.css_first("div.seo-table-row:nth-child(5) div.seo-table-col-2").text()) if parser.css_first("div.seo-table-row:nth-child(5) div.seo-table-col-2") else None,
            "authorized_capital": clean_text(parser.css_first("div.seo-table-row:nth-child(7) div.seo-table-col-2").text()) if parser.css_first("div.seo-table-row:nth-child(7) div.seo-table-col-2") else None,
            "legal_form": clean_text(parser.css_first("p.ucfirst.copy-file-field").text()) if parser.css_first("p.ucfirst.copy-file-field") else None,
            "main_activity": clean_text(" ".join(el.text() for el in parser.css("div.flex-activity span, ul.activities-list li") if el.text())),
            "contact_info": extract_contact_info(" ".join([clean_text(el.text()) for el in parser.css("table.seo-table-item-lg tbody tr td") if el.text()])) if parser.css("table.seo-table-item-lg tbody tr td") else None,
            "authorized_person": clean_text(" ".join(el.text() for el in parser.css("ul.seo-table-list li") if el.text())),
            "tax_info": extract_tax_info(parser),
            "registration_authorities": clean_text(" | ".join(el.text() for el in parser.css("div.info-group p") if el.text())),
            "last_inspection_date": extract_last_inspection_date(parser),
            "company_profile": clean_text(parser.css_first("div.seo-table-generated-text").text()) if parser.css_first("div.seo-table-generated-text") else None,
            "last_updated": datetime.utcnow(),
        }
    elif source == "clarity":
        table = parser.css_first("table.table.align-top.mb-15.border-bottom.w-100")
        if not table:
            logger.error("Data table not found on the Clarity Project page.")
            raise ValueError("Data table not found.")

        rows = table.css("tr")
        clarity_data = []

        for row in rows:
            cells = row.css("td")
            if len(cells) == 2:
                value = clean_text(cells[1].text())
                clarity_data.append(value)
                logger.debug(f"Extracted value: {value}")

        data = {
            "name": clarity_data[1] if len(clarity_data) > 1 else None,
            "code": clarity_data[0] if len(clarity_data) > 0 else company_code,
            "status": clarity_data[4] if len(clarity_data) > 4 else None,
            "registration_date": clarity_data[5] if len(clarity_data) > 5 else None,
            "authorized_capital": clarity_data[6] if len(clarity_data) > 6 else None,
            "legal_form": clarity_data[2] if len(clarity_data) > 2 else None,
            "main_activity": clarity_data[10] if len(clarity_data) > 10 else None,
            "contact_info": clarity_data[3] if len(clarity_data) > 3 else None,
            "authorized_person": clarity_data[6] if len(clarity_data) > 6 else None,
            "tax_info": clarity_data[8] if len(clarity_data) > 8 else None,
            "registration_authorities": clean_registration_authorities(clarity_data[9]) if len(clarity_data) > 9 else None,  # Реєстраційні органи
            "last_inspection_date": None,
            "company_profile": None,
            "last_updated": datetime.utcnow(),
        }

    logger.info(f"Parsed data for company {company_code} from {source}: {data}")
    return data
