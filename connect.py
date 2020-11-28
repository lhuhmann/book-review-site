from sqlalchemy import create_engine
from urllib import parse
import os

def sql_connect():
    '''Returns the database engine given a uri'''
    uri = db_uri()
    engine = create_engine(uri)
    return engine

def db_uri():
    '''Generates the uri used to connect to the MySQL database

    Takes no arguments but assumes the existence of a .my.cnf file in the
    same folder as this script with lines beginning with 'host=' defining
    the server, 'user=' defining the username, and 'password=' defining the password.

    Returns:
        str:The uri
    '''
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '.my.cnf')
    file = open(filename)
    for line in file.readlines():
        if line.startswith('host='):
            # the line[:-1] here and below is to avoid including the newline \n character
            server = line[:-1].partition('host=')[2]
        if line.startswith('user='):
            username = line[:-1].partition('user=')[2]
        if line.startswith('password='):
            password = line[:-1].partition('password=')[2]
    database = 'bhuhmann+book-review-site'
    conn_str = f'DRIVER={{MySQL ODBC 8.0 Driver}};SERVER={server};DATABASE={database};USER={username};PASSWORD={password};'
    uri = f'mysql+pymysql://{username}:{password}@{server}/{database}'
    return uri
