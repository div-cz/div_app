import os
import sys
import django
from django.apps import apps
from django.db.models import Q
import asyncio
import aiomysql
import requests
import time
import re
from datetime import date
from unidecode import unidecode
from typing import Dict,Any,Optional
from updated.db_pool import create_db_pool,db_config

api_key="c4efc14c22a10ea59174b7bf4f94310b"

# Přidáme adresář `div_app` přímo do sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',))  # Posuneme se o dvě úrovně výše

# Nastavení DJANGO_SETTINGS_MODULE podle skutečné cesty k nastavení projektu
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'div_config.settings')

# Inicializujeme Django aplikace
django.setup()
from div_content.models import Creator,Metacountry

def validate_date(date_str: str, full_date: bool = True, default_date: Optional[str] = None) -> Optional[int]:
    import datetime
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

def clean_character_name(character_name: str) -> str:
    """
    Clean a character name by removing special characters and excess whitespace.

    Args:
        character_name (str): The character name to clean.

    Returns:
        str: The cleaned character name.
    """
    # Normalize any accented characters (e.g., é -> e)
    cleaned_name = unidecode(character_name)
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name)
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    return cleaned_name.strip().title()

def get_countryid(country_code: str) -> Optional[int]:
    """
    Get the country ID for the given country code.

    Args:
        country_code (str): The country code.

    Returns:
        Optional[int]: The country ID.
    """
    country = Metacountry.objects.filter(
        Q(countrycode__icontains=country_code) |
        Q(countrycode2__icontains=country_code) |
        Q(countryname__icontains=country_code)
    ).values('countryid').first()

    if country:
        return country['countryid']
    return None

def save_creator(creator_data,creator_id):
    name_parts = str(creator_data['name']).split(" ", 1)
    first_name_api = name_parts[0]
    last_name_api = name_parts[1] if len(name_parts) > 1 else first_name_api

    year = validate_date(creator_data.get('birthdate', ''), full_date=False)
    deathdate = validate_date(creator_data.get('deathday', ''), full_date=True)
    url = get_unique_url(creator_data['name'], 'div_content.Creator', 'url', year)
    imdb = creator_data.get('imdb_id', 0)
    popularity = creator_data.get('popularity', 0)
    img_path = creator_data.get('profile_path', 'noimg.png')
    img = img_path if img_path not in [None, ''] else "noimg.png"
    department = creator_data.get('known_for_department', '')
    gender = creator_data.get('gender', '')
    place_of_birth = creator_data.get('place_of_birth', '')
    today = date.today()
    if place_of_birth:
        place = str(place_of_birth).split(',')[-1].strip()
        cleaned_place = clean_character_name(place)
        country_mapping = {
            "UK":231,
            "United Kingdom":231,
            "England":231,
            "Czech Republic":58,
            "Czechoslovakia":58,
            "Danmark":60,
            "Polska":172,
            "United States":232,
            "Italia":106,
                        }
        place_of_birth = country_mapping.get(cleaned_place,get_countryid(cleaned_place) or 0)

    else:
        place_of_birth = 0
    try:
        coutryid = Metacountry.objects.get(countryid=place_of_birth)
    except Metacountry.DoesNotExist:
        coutryid,_  = Metacountry.objects.get_or_create(coutryid=0)[0]
    # print(place_of_birth)
    update_values = {
        "birthdate": year,
        "deathdate":deathdate,
        "imdbid":imdb,
        "popularity":popularity,
        "img":img,
        "knownfordepartment":department,
        "lastupdated":today,
        "gender":gender,
        "countryid":coutryid
    }
    complet_values={
        "creatorid":creator_id,
        "firstname":first_name_api,
        "lastname":last_name_api,
        "url":url,
        **update_values
    }

    author = Creator.objects.filter(creatorid=creator_id).first()

    if author:
        first_name_db,last_name_db = author.firstname,author.lastname
        if first_name_db == first_name_api and last_name_db == last_name_api:
            for key,value in update_values.items():
                setattr(author,key,value)
                print(author.values())

            author.save(update_fields=update_values.keys())
        else:
            for key,value in complet_values.items():
                setattr(author,key,value)

            author.save()

    else:
        Creator.objects.create(**complet_values)


def clean_url(name: str) -> str:
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

def get_unique_url(url: str, table_name: str, column_name: str, year: Optional[int] = None) -> str:
    """
    Generate a unique URL by appending a suffix if necessary using Django ORM.

    Args:
        url (str): The original URL.
        table_name (str): The table name to check uniqueness against.
        column_name (str): The column name to check uniqueness against.
        year (Optional[int], optional): The year to include in the URL. Defaults to None.

    Returns:
        str: The unique URL.
    """
    original_url = clean_url(url)
    try:
        Model = apps.get_model(*table_name.split('.'))
    except LookupError:
        raise ValueError(f"Model '{table_name}' nebyl nalezen.")

    # Check if the original URL is unique
    filter_kwargs = {f"{column_name}": original_url}
    count = Model.objects.filter(**filter_kwargs).count()
    if count == 0:
        return original_url

    # If year is provided, try using URL with year
    if year and year != None:
        url_year = f"{original_url}-{year}"
        filter_kwargs = {f"{column_name}": url_year}
        count = Model.objects.filter(**filter_kwargs).count()
        if count == 0:
            return url_year

        # If not unique, append a number to make it unique
        number = 2
        while True:
            new_url = f"{url_year}-{number}"
            filter_kwargs = {f"{column_name}": new_url}
            count = Model.objects.filter(**filter_kwargs).count()
            if count == 0:
                return new_url
            number += 1

    # If no year is provided, append a number to make it unique
    number = 2
    while True:
        new_url = f"{original_url}-{number}"
        filter_kwargs = {f"{column_name}": new_url}
        count = Model.objects.filter(**filter_kwargs).count()
        if count == 0:
            return new_url
        number += 1

def fetch_data(api_key: str, endpoint: str, entity_id: int) -> Optional[Dict[str, Any]]:
    url = f'https://api.themoviedb.org/3/{endpoint}/{entity_id}?api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {endpoint} ID {entity_id}. Status code: {response.status_code}")
        return None

def add_creator(start_id: int, last_id: int, api_key: str, endpoint: str) -> None:
    if last_id < start_id:
        return

    count = 0
    start_time = time.time()

    try:
        for creator_id in range(start_id,last_id):
            creator_data = fetch_data(api_key, endpoint, creator_id)
            if creator_data:
                save_creator(creator_data, creator_id)
                count += 1
            else:
                print(f"Creator s ID {creator_id} nebyl nalezen.")
    except Exception as e:
        print(f"Neočekávaná chyba během přidávání creator: {e}")
    finally:
        end_time = time.time()
        run_time = end_time - start_time
        print(run_time)

add_creator(5001003,5001010,api_key,'person')
