from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


class Connector:
    # List all class variables here, so they are in one spot.
    conn = None
    cursor = None       # The connection cursor.
    config_file = None  # The file with MySQL credentials.
    section = None      # The section to read from the config file.
    suffix = None

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

    
    def select_other_responses (self, table, fields):
        '''
        Get a dictionrary of fields (keys) and the responses types in
        for an "Other" response (value)
        '''
        d = {}
        data = None

        try:
            for field in fields:
                execute_cmd = f"SELECT {field} FROM {table} WHERE {field} like '%other%'"
                self.cursor.execute(execute_cmd)
                
                data = self.cursor.fetchall()
                
                d[field] = []
                data_lst = [j[0].split(' ') for j in data]
                for item in data_lst:
                    for i in range(1,len(item)):
                        if item[i-1] == 'other':
                            d[field].append(' '.join(item[i:]))
                            break

        except Error as e:
            print(e)

        return d


    def add_suffix(self, suffix):
        if suffix is None:
            return

        if self.suffix is None:
            self.suffix = suffix
        else:
            self.suffix += " " + suffix


    def set_query(self, query):
        # Add the suffix, if there is one.
        if self.suffix is not None:
            if 'WHERE' in query:
                query += ' AND ' + self.suffix
            else:
                query += ' WHERE ' + self.suffix

        self.cursor.execute(query)

       
    def select_count(self, table, field, field_val):
        '''
        Get count of number of rows in specified MySQL table
        where field = field_val
        '''
        data = None
        
        try:
            execute_cmd = f"SELECT COUNT(*) FROM {table} WHERE  {field} REGEXP '(^|.* ){field_val}($| .*)'"
            self.set_query(execute_cmd)
            data = self.cursor.fetchall()[0][0]

        except Error as e:
            print(e)

        return data


    def select_num_rows(self, table):
        ''' Return the number of entries in the database. '''
        data = None

        try:
            self.set_query(f"SELECT COUNT(*) FROM {table}")
            data = self.cursor.fetchall()

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
            self.set_query(f'SELECT * FROM {table}')
            data = self.cursor.fetchall()

        except Error as e:
            print(e)

        return data


    def insert_row(self, table, cols, args):
        '''
        Insert a row into the MySQL specified table.

        table (string): the name of the table insert data into.
        cols (tuple): the names of the columns to insert data into.
        args (tuple): the data to insert; this must match the table's fields.
        '''

        # Remove any quotation marks around the column names.
        strcols = str(cols).replace("'", '').replace('"', '')
        query = f'INSERT INTO {table} {strcols} VALUES {str(args)}'

        try:
            self.cursor.execute(query, ())
            self.conn.commit()

        except Error as e:
            print(e)
