import aiomysql
import os
from typing import Dict, Any
from dotenv import load_dotenv

#load_dotenv()

# Načti konfiguraci databáze z .env souboru
#try:
 #   db_config: Dict[str, Any] = {
 #       'user': os.getenv("DB_USER"),
 #       'password': os.getenv("DB_PASSWORD"),
 #       'host': os.getenv("DB_HOST"),
 #       'database': os.getenv("DB_NAME"),
 #       'port': int(os.getenv("DB_PORT")),
 #   }
 #
 #   api_key: str = os.getenv("API_KEY")

    # Ověř, zda všechny potřebné konfigurační údaje jsou načteny
 #  if not all(db_config.values()):
 #      raise ValueError("Some database configuration values are missing in .env file")

 #  if not api_key:
 #      raise ValueError("API_KEY is missing in .env file")

#except Exception as e:
 #   raise RuntimeError(f"Error loading configuration from .env file: {e}")

async def create_db_pool(db_config: Dict[str, Any]) -> aiomysql.Pool:
    """
    Vytvoří connection pool k databázi pomocí aiomysql.

    Args:
        db_config (Dict[str, Any]): Slovník obsahující konfigurační parametry databáze.

    Returns:
        aiomysql.Pool: Connection pool k databázi.
    """
    try:
        pool = await aiomysql.create_pool(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['database'],
            charset='utf8mb4',
            autocommit=True,
            minsize=1,
            maxsize=30,
        )
        return pool

    except aiomysql.MySQLError as e:
        raise RuntimeError(f"Error creating database connection pool: {e}")