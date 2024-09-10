from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from ebooklib import epub
import os
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ebooks.db'
db = SQLAlchemy(app)

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    cover_path = db.Column(db.String(300), nullable=True)
    epub_path = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), nullable=False)
    genre = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f'<Ebook {self.title} by {self.author}>'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    if query:
        results = Ebook.query.filter(
            (Ebook.title.ilike(f'%{query}%')) |
            (Ebook.author.ilike(f'%{query}%'))
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        results = Ebook.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('search.html', results=results, query=query)

@app.route('/author/<string:author_name>')
def author_books(author_name):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    author = Ebook.query.filter((Ebook.author.ilike(f'%{author_name}'))).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search.html', results=author, query=author_name)

@app.route('/genre/<string:genre_name>')
def search_genre(genre_name):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    genre = Ebook.query.filter((Ebook.genre.ilike(f'%{genre_name}'))).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search.html', results=genre, query=genre_name)

@app.route('/authors')
def authors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    authors = db.session.query(Ebook.author).distinct().order_by(Ebook.author.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('authors.html', authors=authors)

@app.route('/genres')
def genres():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    genres = db.session.query(Ebook.genre).distinct().order_by(Ebook.genre.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('genres.html', genres=genres)

@app.route('/book/<int:ebook_id>')
def book_detail(ebook_id):
    ebook = Ebook.query.get_or_404(ebook_id)
    return render_template('book.html', ebook=ebook)

@app.route('/download/<int:ebook_id>')
def download_ebook(ebook_id):
    ebook = Ebook.query.get_or_404(ebook_id)
    return send_file(ebook.epub_path, as_attachment=True, download_name=f"{ebook.title}.epub")

@app.route('/download_mobi/<int:ebook_id>')
def download_mobi(ebook_id):
    ebook = Ebook.query.get_or_404(ebook_id)
    mobi_filename = f"{ebook.title}.mobi"
    mobi_path = os.path.join('/tmp', mobi_filename)

    try:
        subprocess.run(['ebook-convert', ebook.epub_path, mobi_path], check=True)
        return send_file(mobi_path, as_attachment=True, download_name=mobi_filename)
    except FileNotFoundError:
        return "Conversion tool not found", 500
    except subprocess.CalledProcessError:
        return "Error converting EPUB to MOBI", 500
    finally:
        if os.path.exists(mobi_path):
            os.remove(mobi_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)