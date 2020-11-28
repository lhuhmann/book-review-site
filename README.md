# Book Review Site for CS50

This book review site was developed to meet the criteria for Project 1 of the Harvard class CS50's Web Programming with Python and JavaScript. The project criteria can be found at https://docs.cs50.net/ocw/web/projects/1/project1.html.

## Required Packages

Install from Pipfile.

## Running the app

Run the app with `python book-review-site.py <portnumber>`.

## Code structure

### Scripts used in running the app

* `book-review-site.py` launches the app.
* `app.py` defines the routes.
* `connect.py` provides functions for connecting to the database.
* `request.proxy.py` contains functions for querying the database.
* `forms.py` defines a class for the book search form.
* `access_goodreads.py` provides functions for accessing book reviews via the Goodreads API.

### Scripts used to set up the database

The scripts used to set up the database originally are in the `database_creation` subfolder.

* `books_duplicate_author_removed.csv` contains the data about the books to be uploaded to the database.
* `models.py` defines a class for each database table.
* `create_tables.py` creates the database tables.
* `load_books.py` fills the book, book_author, and author database tables.

### Other folders

* The templates folder contains the html templates for each page of the website.
* The static folder contains JavaScript and CSS files used to style the website.
