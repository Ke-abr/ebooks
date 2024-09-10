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

# TODO
By order of priority
- Add search by first letter for author
- Add genre search
- Add regex for search (example: author:X genre:Y title:Z)
- Add login page
- Add a single or multiple ebook (dont need to run populate everytime)
- Support pdf files (add a button to convert from pdf to epub/mobi)
- Button to trigger the populate
- Button to select a single or multiple books to add
- Edit book data (description, author, title, language, genre)
- Add ways to rate books, add favorites, want to read, already read etc.
- Serve covers without having to copy them in static (takes 2x more space)
- Improve css
