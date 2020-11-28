from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
  '''Class for the database user table'''
  __tablename__ = 'user'
  user_id = db.Column(db.Integer, nullable = False, index = True, primary_key = True, autoincrement = True)
  username = db.Column(db.String(20), nullable = False, unique = True)
  password = db.Column(db.String(20), nullable = False)

class Book(db.Model):
  '''Class for the database book table'''
  __tablename__  = 'book'
  book_id = db.Column(db.Integer, nullable = False, index = True, primary_key = True, autoincrement = True)
  isbn = db.Column(db.String(10), nullable = False, unique = True)
  title = db.Column(db.String(250), nullable = False)
  publication_year = db.Column(db.Integer, nullable = False)

class Author(db.Model):
  '''Class for the database author table'''
  __tablename__ = 'author'
  author_id = db.Column(db.Integer, nullable = False, index = True, primary_key = True, autoincrement = True)
  first_name = db.Column(db.String(25), nullable = False)
  middle_name = db.Column(db.String(25))
  last_name = db.Column(db.String(25))
  full_name = db.Column(db.String(250))

class Book_Author(db.Model):
  '''Class for the database book_author table'''
  __tablename__ = 'book_author'
  book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key = True)
  author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'), primary_key = True)

class Review(db.Model):
  '''Class for the database review table'''
  __tablename__ = 'review'
  review_id = db.Column(db.Integer, nullable = False, index = True, primary_key = True, autoincrement = True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
  book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))
  # Ideally numeric_rating would be an integer, but I haven't figured out how to limit
  # db.Column values to a specific set of integers rather than a specific set of db.db.Strings
  numeric_rating = db.Column(db.Enum("1", "2", "3", "4", "5"), nullable = False)
  review_text = db.Column(db.String(250))
