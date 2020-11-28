import sys
import csv
import os
from flask import Flask, render_template, request

# add the folder containing connect.py to the python path
sys.path.append("..")
from connect import db_uri
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def add_books():
    '''Add books to database.

    Clears the book, author, and book_author tables, then adds
    books from books_duplicate_author_removed.csv to these tables, left
    padding the isbns to replace missing zeros.

    Takes no arguments but assumes the existence of a books_duplicate_author_removed.csv
    in the same folder as this script, where the commas internal to the csv columns
    are replaced with *.

    Returns:
        None
    '''
    # clear the book, author, and book_author tables
    db.session.query(Book_Author).delete()
    db.session.query(Book).delete()
    db.session.query(Author).delete()

    books = open("books_duplicate_author_removed.csv")
    reader = csv.reader(books)
    running_author_list = []
    for isbn, title, authors, year in reader:
        # for some reason isbns are missing their leading zeros, so left pad
        # isbns with zero to reach full 10 digits
        isbn = isbn.zfill(10)
        # add book isbn, title, and year to book table
        book_id = add_book(isbn, title, year)
        # add author(s) to author table and author-book pairs to author_book table
        add_authors(authors, running_author_list, book_id)
    db.session.commit()

def add_book(isbn, title, year):
    '''Add a single book to the database book table
    
    Formats title and adds isbn, title, and publication year of book to
    book table in db.

    Args:
        isbn (str): The book's isbn
        title (str): The book's title
        year (str): The book's publication year

    Returns:
        int:The book_id used as the primary key in the book table
    '''
    # add books to book table
    title = title.replace('*', ',')
    book = Book(isbn=isbn, title=title, publication_year=year)
    db.session.add(book)
    db.session.flush() # flush changes to database so the primary key fields (book_id) is updated
    return book.book_id

def add_authors(authors, running_author_list, book_id):
    '''Add authors of a single book to the book_author and author database tables
    
    Adds all of the authors of the book to the book_author and (if author
    is not already present) author database tables. If the author is already present
    in the author database table, ensures that the existing author_id is used
    when adding the author to the book_author table.
    
    For a given author, if only one name is listed, it
    is assumed to be the author's first name. If two names are listed, they are
    assumed to be the author's first and last names. If three or more names are
    listed, the first is assumed to be the author's first name, the second is
    assumed to be the author's middle name, and the remaining are assumed to be the
    author's last name.

    Args:
        authors (str): A string of author names, separated by *
        running_author_list (list): A list of author dicts that contains the 
            authors who have already been added to the author database table. 
            Each dict in the list has the keys 'author_id' and 'first' and may
            have the additional keys 'middle' and 'last'.
        book_id (str): The book_id of the book associated with the authors

    Returns:
      None
    '''
    author_list = authors.split('*')
    for author_full in author_list:
        author = author_full.split()
        author_dict = {'first':'', 'middle':'', 'last':'', 'full':''}
        author_dict['full'] = author_full
        author_dict['first'] = author[0]
        if len(author) == 2:
            author_dict['last'] = author[1]
        elif len(author) >= 3:
            author_dict['middle'] = author[1]
            author_dict['last'] = ' '.join(author[2:len(author)])
        author_id = add_author_if_new(author_dict, running_author_list)
        # add author_id and book_id to book_author table
        book_author = Book_Author(book_id=book_id, author_id=author_id)
        db.session.add(book_author)

def add_author_if_new(author_dict, running_author_list):
    '''Adds an author to the author database table if they have not already been added

    Args:
        author_dict (dict): A dict describing an author that has the keys
            'author_id' and 'first' and may have the additional keys 'middle' and 'last'.
        running_authorlist (list): A list of authors that have already been added to
            the author database table

    Returns:
        int:The author_id used as the primary key in the author table and as part of the
            two-column primary key in the book_author table
    '''
    existing_author_id = get_existing_author_id(author_dict, running_author_list)
    if existing_author_id:
        author_id = existing_author_id
    else:
        author = Author(
            first_name = author_dict['first'],
            middle_name = author_dict['middle'],
            last_name = author_dict['last'],
            full_name = author_dict['full'])
        db.session.add(author)
        db.session.flush() # flush changes to database so the primary key field (author_id) is updated
        author_id = author.author_id
        author_dict['author_id'] = author_id
        running_author_list.append(author_dict)
    return author_id

def get_existing_author_id(author, running_author_list):
    '''Returns author_id for specified author if it exists

    If the specified author already exists in running_author_list, 
    returns that author's author_id. Otherwise returns None.

    Args:
        author (dict): A dict describing an author that has the keys
            'author_id' and 'first' and may have the additional keys 'middle' and 'last'.
        running_authorlist (list): A list of authors that have already been added to
            the author database table

    Returns:
        int:The author_id used as the primary key in the author table or None if
            an author_id does not yet exist for this author.
    '''
    for existing_author in running_author_list:
        if author['first'] == existing_author['first'] and author['middle'] == existing_author['middle'] and author['last'] == existing_author['last']:
            return existing_author['author_id']

if __name__ == "__main__":
    with app.app_context():
        add_books()
