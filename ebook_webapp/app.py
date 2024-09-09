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
    book_metadata = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Ebook {self.title} by {self.author}>'

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)