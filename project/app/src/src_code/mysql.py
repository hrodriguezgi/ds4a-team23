"""
MySQL class


date        author              changelog
2022-06-23  hrodriguezgi        creation
"""

from sqlalchemy import create_engine
import pandas as pd


class MySQL:
    def __init__(self) -> None:
        self.cnx = create_engine("mysql+pymysql://root:1234@localhost/ds4a?charset=utf8mb4")

    def read_sql(self, sql, params=None):
        if params is None:
            params = {}

        data = pd.read_sql(sql.format(**params), self.cnx)
        return data

    def insert_sql(self, df, table_name, mode='append'):
        df.to_sql(table_name.lower(),
                  con=self.cnx,
                  index=False,
                  if_exists=mode,
                  method='multi')
