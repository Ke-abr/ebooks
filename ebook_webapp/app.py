from flask import Flask, render_template, request, send_file, redirect, url_for
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
    if query:
        results = Ebook.query.filter(
            (Ebook.title.ilike(f'%{query}%')) |
            (Ebook.author.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('search.html', results=results, query=query)

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