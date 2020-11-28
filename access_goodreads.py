import json
import requests
import subprocess
import sys
from pathlib import Path

def get_goodreads_book(isbn):
    '''Return goodreads.com reviews for a given book

    Assumes that a goodreads_api_key.txt file containing the
    API key for goodreads.com exists in the same file as this script.

    Args:
        isbn (str): The ISBN for the book of interest 
    '''
    goodreads_api_key = Path('goodreads_api_key.txt').read_text()
    goodreads_json = get_book_reviews(function = 'review_counts.json',
                                      params = f'isbns={isbn}',
                                      key = goodreads_api_key)
    goodreads_book = goodreads_json['books'][0]
    return goodreads_book

def get_book_reviews(function, params, key, 
                     site='https://www.goodreads.com/book/'):
    '''Access book review information from goodreads.com.
      
    Args:
        function (str): goodreads.com functional directives
        params (str): Additional url parameters
        key (str): User's API key for the specified site
        site (str): The website url (default https://www.goodreads.com/book/)
   
    Returns:
       Results of the API call
    '''
    url = site + function + '?'  + params + '&key=' + key
    response = requests.get(url)
    return json.loads(response.content.decode())
