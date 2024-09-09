# ebooks
WebApp to list and download ebooks

# Prerequisites
Install the following packages:
- install python3 python3-pip calibre
- pip3 install Flask Flask_SQLAlchemy EbookLib


# How to use
- Change the path in populate_db.py
- Run python3 app.py a first time to create the sqlite database schema, close the app after
- Run python3 populate_db.py to import data in the db and create the covers in static/covers
- Run python3 app.py to access the web app

# Note
The populate_db.py assume the ebook is in epub format and the path is the following:

path/author/title/"title - author.epub"
The conversion to mobi is done in app.py