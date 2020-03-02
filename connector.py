from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


class Connector:
    # List all class variables here, so they are in one spot.
    conn = None
    cursor = None       # The connection cursor.
    config_file = None  # The file with MySQL credentials.
    section = None      # The section to read from the config file.

    def __init__(self, config='config.ini', section='mysql'):
        self.config_file = config
        self.section = section

        # Try connecting.
        self.__connect()

    def __del__(self):
        # Close the connection.
        if self.conn is not None and self.conn.is_connected():
            print('Connection closed')
            self.conn.close()


    def __read_db_config(self):
        '''
        Read the database config file and return a dictionary of the read values.
        '''

        # Read the config file.
        parser = ConfigParser()
        parser.read(self.config_file)

        # Read the desired section.
        db = {}

        if parser.has_section(self.section):
            items = parser.items(self.section)

            for item in items:
                db[item[0]] = item[1]

        else:
            raise Exception(f'{self.section} not found in the file {self.config_file}')

        return db


    def __connect(self):
        '''
        Try connecting to the MySQL database with credentials given in
        self.config_file.
        '''

        db_config = self.__read_db_config()

        try:
            print('Connecting to database ...')
            self.conn = MySQLConnection(**db_config)

            if self.conn.is_connected():
                print('Connection established')
                self.cursor = self.conn.cursor()
            else:
                print('Connection failed')

        except Error as error:
            print(error)


    def select_count(self, table, field, field_val):
        '''
        Get count of number of rows in specified MySQL table
        where field = field_val
        '''
        data = None
        
        try:
            execute_cmd = f"SELECT COUNT(*) FROM {table} WHERE  {field} REGEXP '(^|.* ){field_val}($| .*)'"
            print('\n' + execute_cmd + '\n')
            self.cursor.execute(execute_cmd)
            data = self.cursor.fetchall()[0][0]
            print(f'Num rows where {field}={field_val}: {data}')

        except Error as e:
            print(e)

        return data

    def select_all_data(self, table):
        '''
        Get all data from the specified MySQL table.

        table (string): the name of the table to read data from.
        '''

        data = None

        try:
            self.cursor.execute(f'SELECT * FROM {table}')
            data = self.cursor.fetchall()

        except Error as e:
            print(e)

        return data


    def insert_row(self, table, args):
        '''
        Insert a row into the MySQL specified table.

        table (string): the name of the table insert data into.
        args (tuple): the data to insert; this must match the table's fields.
        '''

        query = f'INSERT INTO {table} VALUES ' + str(args)

        try:
            self.cursor.execute(query, ())
            self.conn.commit()

        except Error as e:
            print(e)
