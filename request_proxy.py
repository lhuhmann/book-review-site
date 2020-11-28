import connect
import numpy as np
import pandas as pd
import sys
from sqlalchemy import Table, Column, insert, MetaData, and_, text, func

from database_creation.models import User, Book, Author, Book_Author, Review

engine = connect.sql_connect()

def get_dict_list_from_result(result):
    '''Turns a sqlalchemy.util._collections.result object into a list of dicts
    
    Args:
    result (sqlalchemy.util._collections): An object resulting from using
        to query the database

  Returns:
    dict:The input object reformatted as a list of dict. Each dict represents a single
        row in the database table, with the dict keys mapping to the database column
        names.
    '''
    list_dict = []
    for i in result:
        i_dict = i._asdict()
        list_dict.append(i_dict)
    return list_dict

def get_all_books(db):
    '''Returns all books with their associated information.
    
    Args:
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        sqlalchemy.util._collections: For each book in the database,
            the isbn, title, publication_year, author first_name,
            author middle_name, and author last_name.
    '''
    books = db.session.query(Book, Book_Author, Author
        ).filter(Book.book_id == Book_Author.book_id
        ).filter(Author.author_id == Book_Author.author_id
        ).with_entities(Book.isbn, Book.title, Book.publication_year,
        Author.first_name, Author.middle_name, Author.last_name)
    return books

def get_searched_books(param_dict, db):
    '''Returns book(s) that match user search.
    
    Args:
        param_dict (dict): The user-specified search parameters
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        dict: A dict of books matching the user-specified search parameters
            with isbn, title, publication_year, author first_name, author
            middle_name, and author last_name for each book
    '''
    conditions = []
    for key, value in param_dict.items():
        if value != '':
            # want to ensure that first part of the db string matches the user-submitted value
            # but it's okay if the db string continues past that
            value = value + '%'
            if (key == 'last_name' or key == 'first_name'):
                conditions.append(getattr(Author, key).like(value))
            else:
                conditions.append(getattr(Book, key).like(value))
    books = db.session.query(
            Book.isbn,
            Book.title,
            Book.publication_year,
            func.group_concat(Author.full_name).label('authors')
        ).filter(Book.book_id == Book_Author.book_id
        ).filter(Author.author_id == Book_Author.author_id
        ).filter(and_(*conditions)
        ).group_by(Book.book_id)
    return get_dict_list_from_result(books)

def get_book_by_isbn(isbn, db):
    '''Returns book(s) that match user search.
    
    Args:
        isbn: The book's ISBN
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        dict: None if no match was found; otherwise a dict with
            book_id, isbn, title, publication_year, author first_name, author
            middle_name, and author last_name for the matching book
    '''
    book = db.session.query(
            Book.book_id,
            Book.isbn,
            Book.title,
            Book.publication_year,
            func.group_concat(Author.full_name).label('authors')
        ).filter(Book.book_id == Book_Author.book_id
        ).filter(Author.author_id == Book_Author.author_id
        ).filter(Book.isbn == isbn
        )
    if not get_dict_list_from_result(book):
        return None
    # we only expect one dict in the list, so we take the first item
    return get_dict_list_from_result(book)[0]

def verify_user(username, password, db):
    '''Returns user_id associated with submitted password and username.
    Args:
        username: The user's username
        password: The user's password
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        dict: A dict containing the user_id for the user
    '''
    user = User.query.filter_by(username = username, password = password).with_entities(User.user_id)
    return get_dict_list_from_result(user)

def new_username(username, db):
    '''Checks whether username exists in database
    
    Args:
        username: The user's username
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        bool: True if username is not in database (i.e. is new);
        False if username is in database
    '''
    tb = User.query.filter_by(username = username).all()
    return not tb

def add_user(username, password, db):
    '''Adds user to users table in database.
        
    Args:
        username: The user's username
        password: The user's password
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        None
    '''
    user = User(username = username, password = password)
    db.session.add(user)

def check_and_add_user(username, password, db):
    '''Check if username is unique and add user if so
    
    Args:
        username: The user's username
        password: The user's password
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        bool: True if user is successfully added; False if
            username already exists and user is not added
    '''
    unique_user = new_username(username, db)
    if unique_user:
        add_user(username, password, db)
    db.session.commit()
    return unique_user

def not_yet_reviewed(user_id, book_id, db):
    '''Returns true when user has *not* previously reviewed the book with book_id.
    
    Args:
        user_id: The user_id (used as the primary key in the user database table)
        book_id: The book_id (used as the primary key in the book database table)
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        bool: True if book has not yet been reviewed by this user; False otherwise
    '''
    user = Review.query.filter_by(user_id = user_id, book_id = book_id).with_entities(User.user_id)
    return not get_dict_list_from_result(user)

def add_review(user_id, book_id, rating, review_text, db):
    '''If user has not previously reviewed this book, add the user's review to the database
    
    Args:
        user_id: The user_id (used as the primary key in the user database table)
        book_id: The book_id (used as the primary key in the book database table)
        rating: The user's rating of the book on a scale of 1-5
        review_text: The user's textual review of the book
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        None
    '''
    # first check if a review by this user exists
    not_reviewed = not_yet_reviewed(user_id, book_id, db)
    if not_reviewed:
        # Add review to database
        review = Review(user_id = user_id,
                        book_id = book_id,
                        numeric_rating = rating,
                        review_text = review_text)
        db.session.add(review)
        db.session.commit()

def get_reviews(book_id, db):
    '''Get all user reviews for the given book_id
    
    Args:
        book_id: The book_id (used as the primary key in the book database table)
        db: The flask_sqlalchemy.SQLAlchemy object used to
            interact with the database

    Returns:
        dict: A list of dictionaries for each user review of the book,
            with keys username, numeric_rating, and review text; 
            None if no reviews exist for the book with this book_id
    '''
    review = db.session.query(User, Review
        ).filter(User.user_id == Review.user_id
        ).filter(Review.book_id == book_id
        ).with_entities(User.username, Review.numeric_rating, Review.review_text)
    if not get_dict_list_from_result(review):
        return None
    return get_dict_list_from_result(review)
