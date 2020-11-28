import sys
import requests
from flask import (Flask, render_template, send_from_directory, request, 
                   redirect, flash, session, url_for, jsonify)
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

import request_proxy
import forms
from connect import db_uri
from access_goodreads import get_goodreads_book

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = Path('flask_secret_key.txt').read_text()
db.init_app(app)

@app.route('/')
def home():
    '''Redirect to login page'''
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    '''Log in user'''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username:
            flash('Please supply a username', 'error')
            return render_template('login.html')
        elif not password:
            flash('Please supply a password', 'error')
            return render_template('login.html')
        else:
            # the returned user_list will have either zero or one items in it
            user_list = request_proxy.verify_user(username, password, db)
            if user_list:
                # the sql query returns a list; user is the first (and only) item in it
                user = user_list[0]
                session.clear()
                session['username'] = username
                session['user_id'] = user['user_id']
                return redirect(url_for('render_search'))
            else:
                flash('The submitted username or password is incorrect', 'error')
                return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    '''Register user'''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmed_password = request.form['confirmed_password']
        if not username:
            flash('Please supply a username', 'error')
            return render_template('register.html')
        elif (not password or not confirmed_password):
            flash('Please supply and confirm a password', 'error')
            return render_template('register.html')
        elif password != confirmed_password:
            flash('Supplied passwords do not match', 'error')
            return render_template('register.html')
        else:
            unique_username = request_proxy.check_and_add_user(username, password, db)
            if not unique_username:
                flash('The supplied username is already in use', 'error')
                return render_template('register.html')
            else:
                flash('Registration successful!', 'error')
                return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    '''Log out user'''
    session.clear()
    flash('Logout successful', 'error')
    return redirect(url_for('login'))

@app.route('/books')
def show_books():
    '''Show table with info for all books in database'''
    books = request_proxy.get_all_books(db)
    return render_template('books.html', books=books)

@app.route('/api/<string:isbn>')
def get_book_json(isbn):
    '''Provide JSON with info from database and Goodreads for the book with the specified isbn'''
    # Get book and review info from db
    book = request_proxy.get_book_by_isbn(isbn, db)
    print(book, file=sys.stderr)
    if book is None:
        return jsonify({'error': 'There is no book with this ISBN in the database'}), 404

    # Get review info from Goodreads
    goodreads_book = get_goodreads_book(isbn)

    return jsonify({
        'title': book['title'],
        'authors': book['authors'],
        'year': book['publication_year'],
        'isbn': book['isbn'],
        'review_count': goodreads_book['ratings_count'],
        'average_score': goodreads_book['average_rating']
    })

@app.route('/books/<string:isbn>', methods = ['GET', 'POST'])
def show_book(isbn):
    '''Display info about and provide option to review book with the specified isbn.'''
    # Get book and review info from db
    book = request_proxy.get_book_by_isbn(isbn, db)
    print(book, file=sys.stderr)
    if not book:
        return('No book with the specified ISBN exists in the database')

    reviews = request_proxy.get_reviews(book['book_id'], db)
    # Only show reviews table if reviews exist
    show_reviews = False
    if reviews:
        show_reviews = True

    goodreads_book = get_goodreads_book(isbn)

    # only show review form if user is logged in
    show_form = False
    if session.get('user_id'):
        not_reviewed = request_proxy.not_yet_reviewed(session['user_id'], book['book_id'], db)
        # only show review form if user hasn't previously submitted a review for this book
        if not_reviewed:
            show_form = True
    if request.method == 'POST':
        request_proxy.add_review(user_id = session['user_id'],
                                book_id = book['book_id'],
                                rating = request.form['rating'],
                                review_text = request.form['review_text'],
                                db = db)
        return render_template('review.html',
                                book = book,
                                goodreads_num_ratings = goodreads_book['ratings_count'],
                                goodreads_avg_rating = goodreads_book['average_rating'],
                                show_form = False,
                                show_reviews = True,
                                reviews = request_proxy.get_reviews(book['book_id'], db))
    else:
        return render_template('review.html',
                                book = book,
                                goodreads_num_ratings = goodreads_book['ratings_count'],
                                goodreads_avg_rating = goodreads_book['average_rating'],
                                show_form = show_form,
                                show_reviews = show_reviews,
                                reviews = reviews)

@app.route('/search', methods = ['GET'])
def render_search():
    '''Allow user to search books'''
    f = forms.BookSearchForm(request.args)
    # Don't search and show results if form hasn't been submitted or if empty form is submitted
    if not request.args or all(value == '' for value in request.args.values()):
        return render_template('search.html', form=f, books = None, show_table=False)
    else:
        books = request_proxy.get_searched_books(request.args, db)
        if not books:
            flash('No books match the search criteria', 'error')
            return render_template('search.html', form=f, books = books, show_table=False)
        return render_template('search.html', form=f, books = books, show_table=True)
