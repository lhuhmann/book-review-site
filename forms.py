from flask_wtf import FlaskForm
from wtforms import StringField
  
class BookSearchForm(FlaskForm):
    isbn = StringField("ISBN")
    title = StringField("Title")
    last_name = StringField("Author Last Name")
    first_name = StringField("Author First Name")
