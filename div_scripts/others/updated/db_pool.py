import aiomysql
import os
from typing import Dict, Any
from dotenv import load_dotenv

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