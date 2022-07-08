from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import pandas as pd


class PostgreSQL:
    def __init__(self) -> None:
        """
        Constructor for the class.
        """
        self.url = config('DATABASE_URL')

        try:
            self.connection = create_engine(self.url)
        except OperationalError as err:
            print("I am unable to connect to the database, {}".format(err))
            raise err

    def read_sql(self, sql, params=None):
        """
        Executes the data associated to a query.
        sql->The query to be executed
        params->Parameters to enhance the query
        """
        if params is None:
            params = {}

        # Execute the query and saves the data for further use
        data = pd.read_sql(sql.format(**params), self.connection)
        return data

    def insert_sql(self, df, table_name, mode='append'):
        """
        Executes an insert query.
        df->It's the dataframe that contains the data to be saved
        table_name->It's the table in the database where the data is
        mode->Specifies the mode of insertion. It appends by default.
        """
        # It saves the dataframe to the database
        df.to_sql(table_name.lower(),
                  con=self.connection,
                  index=False,
                  if_exists=mode,
                  method='multi')


def main():
    """
    Instantiates the class PostgreSQL and extracts the agents information
    """
    psql = PostgreSQL()
    uvw_agents = psql.read_sql("""select * from uvw_agents limit 50""")
    print(uvw_agents.head())


if __name__ == '__main__':
    main()
