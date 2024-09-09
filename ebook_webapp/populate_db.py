from app import db, Ebook
from ebooklib import epub
from app import app
import os

EBOOK_DIR = '/mnt/h/DL/testCollection'

COVER_DIR = os.path.join('static', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

def extract_metadata(epub_path):
    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Unknown Title'
    author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else 'Unknown Author'
    description = book.get_metadata('DC', 'description')[0][0] if book.get_metadata('DC', 'description') else "No Description"
    language = book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "Unknown Language"
    genre = book.get_metadata('DC', 'subject')[0][0] if book.get_metadata('DC', 'subject') else "Unknown Genre"
    return title, author, description, language, genre

def extract_cover(epub_path, book_id):
    book = epub.read_epub(epub_path)
    cover = book.get_item_with_id('cover')
    if not cover:
        for item in book.get_items():
            if 'cover' in item.get_name().lower():
                cover = item
                break
    if cover:
        cover_filename = f"cover_{book_id}.jpg"
        cover_path = os.path.join(COVER_DIR, cover_filename)
        with open(cover_path, 'wb') as f:
            f.write(cover.get_content())
        return cover_path
    return None

# Ugly shit, can probably do better
def populate_database():
    with app.app_context():
        for author in os.listdir(EBOOK_DIR):
            author_path = os.path.join(EBOOK_DIR, author)
            if os.path.isdir(author_path):
                for book_title in os.listdir(author_path):
                    book_path = os.path.join(author_path, book_title)
                    if os.path.isdir(book_path):
                        for epub in os.listdir(book_path):
                            if epub.endswith(".epub"):
                                epub_file = os.path.join(book_path, epub)
                                if os.path.exists(epub_file):
                                    title, author_name, description, language, genre = extract_metadata(epub_file)
                                    ebook = Ebook(title=title, author=author_name, description=description, language=language, genre=genre, epub_path=epub_file)
                                    db.session.add(ebook)
                                    db.session.commit()
                                    cover_path = extract_cover(epub_file, ebook.id)
                                    if cover_path:
                                        ebook.cover_path = cover_path
                                        db.session.commit()
                                    print(f"Added: {title} by {author_name}")

if __name__ == '__main__':
    populate_database()
