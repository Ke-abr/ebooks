from app import db, Ebook
from ebooklib import epub
from ebooklib.epub import EpubException
from zipfile import BadZipFile
from app import app
import os
import re
import shutil

EBOOK_DIR = '/mnt/h/DL/ebookCollection/ebookCollection'
COVER_DIR = os.path.join('static', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

def extract_metadata(epub_path):
    # Get the author and title from the filename
    base_name = os.path.basename(epub_path).replace('.epub', '')
    match = re.match(r'(.*) - (.*)', base_name)
    if match:
        title = match.group(1)
        author = match.group(2)
    try:
        # Get the infos from the epub metadata
        book = epub.read_epub(epub_path)
        description = book.get_metadata('DC', 'description')[0][0] if book.get_metadata('DC', 'description') else "No Description"
        if not description:
            description = "Unknwon Description"
        language = book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "Unknown Language"
        if not language:
            language = "Unknwon Language"
        genre = book.get_metadata('DC', 'subject')[0][0] if book.get_metadata('DC', 'subject') else "Unknown Genre"
        if not genre:
            genre = "Unknown Genre"
        return title, author, description, language, genre
    except (EpubException, KeyError, AttributeError, BadZipFile, IndexError, TypeError) as e:
        print(f"Error reading {epub_path}: {str(e)}")
        return title, author, "No Description", "Unknown Language", "Unknown Genre"

def extract_cover(epub_path, book_id):
    try:
        book = epub.read_epub(epub_path)
        cover = book.get_item_with_id('cover')
        cover_filename = f"cover_{book_id}.jpg"
        cover_path = os.path.join(COVER_DIR, cover_filename)

        # If cover not found with id 'cover', search all items for cover
        if not cover:
            for item in book.get_items():
                if 'cover' in item.get_name().lower():
                    cover = item
                    break
        # If cover is found, save it to cover directory and return the path
        if cover:
            with open(cover_path, 'wb') as f:
                f.write(cover.get_content())
            return cover_path
        
        # If cover is not found at all, copy the cover.jpg file from the epub directory and return the path
        external_cover_path = os.path.join(epub_path, 'cover.jpg')
        if os.path.exists(external_cover_path):
            shutil.copy(external_cover_path, cover_path)
            return cover_path
        
        # If no cover is found return the default cover
        return os.path.join(COVER_DIR, 'default.jpg')
    
    except (EpubException, KeyError, AttributeError, BadZipFile, IndexError, TypeError) as e:
        print(f"Error getting cover {epub_path}: {str(e)}")
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
                                    existing_ebook = Ebook.query.filter_by(epub_path=epub_file).first()
                                    if not existing_ebook:
                                        title, author_name, description, language, genre = extract_metadata(epub_file)
                                        ebook = Ebook(title=title, author=author_name, description=description, language=language, genre=genre, epub_path=epub_file)
                                        db.session.add(ebook)
                                        db.session.commit()
                                        cover_path = extract_cover(epub_file, ebook.id)
                                        if cover_path:
                                            ebook.cover_path = cover_path
                                            db.session.commit()
                                        print(f"Added: {title} by {author_name}")
                                    else:
                                        print(f"Skipping: {existing_ebook.title} by {existing_ebook.author} (already exists)")

if __name__ == '__main__':
    populate_database()
