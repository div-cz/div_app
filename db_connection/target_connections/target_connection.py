import os

from pyspark.shell import spark
from pyspark.sql import DataFrame


class TargetConnection:
    def __init__(self):
        self.db_host: str = os.getenv('TARGET_DB_HOST')
        self.db_name: str = os.getenv('TARGET_DB_NAME')

    def load_data_from_db(self, table_name: str) -> DataFrame:
        return spark.read.format("jdbc")\
            .option("url", f"jdbc:mysql://{self.db_host}/{self.db_name}") \
            .option("driver", "com.mysql.jdbc.Driver")\
            .option("dbtable", table_name) \
            .option(os.getenv('TARGET_DB_USER'), "root")\
            .option(os.getenv('TARGET_DB_PASSWORD'), "root").load()

    def get_data_for_table(self):
        pass

    def get_foreign_key(self, meta_table_name):
        pass
