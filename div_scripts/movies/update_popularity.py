def batch():
    from dotenv import load_dotenv
    import os
    import requests
    import mysql.connector
    from mysql.connector import Error
    import time

    # Virtualni prostředí
    load_dotenv()

    # Nastavení TMDB API
    api_key = os.getenv("API_KEY")
    base_url = 'https://api.themoviedb.org/3/movie/{id}?api_key=' + api_key + "&language=cs-CZ"

    # Nastavení připojení k databázi

    db_config_test = {
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'host': os.getenv("DB_HOST"),
        'database': os.getenv("DB_NAME")
    }

    # Připojení k databázi
    try:
        conn = mysql.connector.connect(**db_config_test)
        cursor = conn.cursor()
        print("Úspěšně připojeno k databázi.")
    except Error as e:
        print(f"Chyba při připojování k databázi: {e}")
        exit()
    # Zapnutí časovače
    start_time = time.time()

    # Vytvoření pole pro dávkové vkládání do DB
    update_data = []

    try:
        for film_id in range(2250, 2350):
            response = requests.get(url=base_url.format(id=film_id))
            if response.status_code == 200:
                data = response.json()
                update_data.append((data.get('popularity', 0), data['id']))

                # Aktualizace popularit v dávce po 50 filmech
                if len(update_data) >= 50:
                    cursor.executemany("UPDATE Movie SET Popularity = %s WHERE MovieID = %s", update_data)
                    conn.commit()
                    print(f"Popularity pro {len(update_data)} filmů byla aktualizována.")
                    update_data = []  # Vyprázdnění seznamu pro další filmy

            else:
                print(f"TMDB Movie with ID {film_id} not found or request failed.")

        # Zbývající filmy v dávce
        if update_data:
            cursor.executemany("UPDATE Movie SET Popularity = %s WHERE MovieID = %s", update_data)
            conn.commit()
            print(f"Popularity pro zbylých {len(update_data)} filmů byla aktualizována.")

    except Exception as err:
        print("Error: ", err)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Celková doba běhu skriptu: {total_time} sekund.")

batch()