
"""
MySQL class


date        author              changelog
2022-06-23  hrodriguezgi        creation
"""

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import pandas as pd

class PostgreSQL:
    def __init__(self) -> None:
        self.url = f"postgresql://FelixDavid12:v2_3s8Wd_jxbz2wSxRAcdKxkaCKkMztE@db.bit.io:5432/FelixDavid12/ds4a-team-23?sslmode=require"

        try:
            self.connection = create_engine(self.url)
        except OperationalError as err:
            print("I am unable to connect to the database, {}".format(err))
            raise err


    def read_sql(self, sql, params=None):
        if params is None:
            params = {}
        
        data = pd.read_sql(sql.format(**params), self.connection)
        return data


def main():
    psql = PostgreSQL()
    conteo = psql.read_sql("""select * from uvw_agents limit 50""")
    print(conteo.head())

if __name__ == '__main__':
    main()