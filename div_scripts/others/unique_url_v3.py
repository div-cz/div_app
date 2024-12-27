from datetime import datetime
import aiofiles
import aiomysql
import regex
import re
from unidecode import unidecode
import json
from html import unescape
from typing import Optional, Tuple
import logging


async def validate_date(date_str: str, full_date: bool = True, default_date: Optional[str] = None) -> Optional[int]:
    """
    Validate the given date string.

    Args:
        date_str (str): The date string to validate.
        full_date (bool, optional): Whether to validate the full date. Defaults to True.
        default_date (Optional[str], optional): The default date to return if validation fails. Defaults to None.

    Returns:
        Optional[int]: The validated date string or default date.
    """
    try:
        if not full_date:
            if date_str:
                return int(date_str.split('-')[0])
            else:
                return None
        elif date_str:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
    except:
        if not full_date:
            return None
        else:
            pass
    return default_date


async def get_uniqueurl_v2(conn: aiomysql.Connection, url: str, table_name: str, column_name: str, year: Optional[int] = None) -> str:
    """
    Generate a unique URL by appending a suffix if necessary.

    Args:
        conn (aiomysql.Connection): The database connection
        url (str): The original URL.
        table_name (str): The table name to check uniqueness against.
        column_name (str): The column name to check uniqueness against.
        year (Optional[int], optional): The year to include in the URL. Defaults to None.

    Returns:
        str: The unique URL.
    """
    original_url = await clean_url(url)
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = %s"

    async with conn.cursor() as cursor:
        await cursor.execute(query, (original_url,))
        count = await cursor.fetchone()
        if count[0] == 0:
            return original_url

        if year:
            url_year = f"{original_url}-{year}"
            await cursor.execute(query, (url_year,))
            count = await cursor.fetchone()
            if count[0] == 0:
                return url_year

            number = 2
            while True:
                new_url = f"{url_year}-{number}"
                await cursor.execute(query, (new_url,))
                count = await cursor.fetchone()
                if count[0] == 0:
                    return new_url
                number += 1

        number = 2
        while True:
            new_url = f"{original_url}-{number}"
            await cursor.execute(query, (new_url,))
            count = await cursor.fetchone()
            if count[0] == 0:
                return new_url
            number += 1


async def is_latin(text: str) -> bool:
    """
    Check if the text contains only Latin characters.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if the text contains only Latin characters, False otherwise.
    """
    latin_pattern = r'^[\p{Latin}\s\d\p{Punctuation}]*$'
    return bool(regex.fullmatch(latin_pattern, text))


async def clean_url(name: str) -> str:
    """
    Clean the given URL by replacing special characters and normalizing.

    Args:
        name (str): The URL to clean.

    Returns:
        str: The cleaned URL.
    """
    name = name.replace('я', 'ja')
    name = re.sub(r'[\'\.\,\/:#()°]', '-', name)
    name_ascii = unidecode(name)
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s-]', '', name_ascii)
    new_cleaned_name = re.sub(r'[\s-]+', '-', cleaned_name).lower()
    new_cleaned_name = new_cleaned_name[:200].rstrip('-').lstrip('-')
    return new_cleaned_name

async def get_countryid(pool, country_code: str) -> int:
    """
    Get the country ID for the given country code.

    Args:
        pool: Database connection pool.
        country_code (str): The country code.

    Returns:
        int: The country ID.
    """
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            query = "SELECT CountryID FROM MetaCountry WHERE CountryCode2 = %s"
            await cursor.execute(query, (country_code,))
            result = await cursor.fetchone()
            if result:
                return result[0]
            else:
                return 0

async def split_name(name: str) -> Tuple[str, str]:
    """
    Split a full name into first and last name.

    Args:
        name (str): The full name to split.

    Returns:
        Tuple[str, str]: A tuple containing the first and last name.
    """
    parts = name.split(' ', 1)
    return parts if len(parts) > 1 else (name, name)

async def clean_character_name(character_name: str) -> str:
    """
    Clean a character name by removing special characters and excess whitespace.

    Args:
        character_name (str): The character name to clean.

    Returns:
        str: The cleaned character name.
    """
    cleaned_name = unidecode(character_name)
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name)
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    cleaned_name = cleaned_name.replace(' ', '_')
    return cleaned_name.strip()

async def save_to_file(filename: str, data: dict):
    """
    Save data to a file in JSON format.

    Args:
        filename (str): The file name.
        data (dict): The data to save.
    """
    async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
        json_data = json.dumps(data, ensure_ascii=False)
        await f.write(json_data + '\n')

async def clean_text(text: str) -> str:
    """
    Clean text by removing HTML tags and unescaping HTML entities.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    text = unescape(text)
    return text

async def check_exists(pool: aiomysql.Pool, table: str, table_row: str, record_id: int) -> bool:
    """
    Check if a record exists in the specified table of the database.

    Args:
        pool (aiomysql.Pool): The database connection pool.
        table (str): The name of the table to check.
        table_row (str): The column name to check.
        record_id (int): The ID of the record to check.

    Returns:
        bool: True if the record exists, False otherwise.
    """
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT 1 FROM {table} WHERE {table_row} = %s", (record_id,))
            exists = await cursor.fetchone()
            return bool(exists)