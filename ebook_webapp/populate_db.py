from app import db, Ebook
from ebooklib import epub
from ebooklib.epub import EpubException
from zipfile import BadZipFile
from app import app
from concurrent.futures import ThreadPoolExecutor
import os
import re
import shutil
import logging

logging.basicConfig(filename='ebook_import.log', level=logging.DEBUG)

EBOOK_DIR = '/mnt/h/DL/ebookCollection/ebookCollection'
COVER_DIR = os.path.join('static', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

def extract_metadata(epub_path):
    # Get the author and title from the filename
    base_name = os.path.basename(epub_path).replace('.epub', '')
    match = re.match(r'(.*) - (.*)', base_name)
    title, author = match.groups() if match else (None, None)
    try:
        # Get the infos from the epub metadata
        book = epub.read_epub(epub_path)
        description = book.get_metadata('DC', 'description')[0][0] if book.get_metadata('DC', 'description') else "No Description"
        language = book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "Unknown Language"
        if not language:
            language = "Unknown Language"
        genre = book.get_metadata('DC', 'subject')[0][0] if book.get_metadata('DC', 'subject') else "Unknown Genre"
        if not genre:
            genre = "Unknown Genre"
        return title, author, description, language, genre
    except (EpubException, KeyError, AttributeError, BadZipFile, IndexError, TypeError) as e:
        logging.error(f"Error reading {epub_path}: {str(e)}")
        return title, author, "No Description", "Unknown Language", "Unknown Genre"

def extract_cover(epub_path, book_id):
    cover_filename = f"cover_{book_id}.jpg"
    cover_path = os.path.join(COVER_DIR, cover_filename)

    try:
        book = epub.read_epub(epub_path)
        cover = book.get_item_with_id('cover')

        if not cover:
            for item in book.get_items():
                if 'cover' in item.get_name().lower():
                    cover = item
                    break

        if cover:
            with open(cover_path, 'wb') as f:
                f.write(cover.get_content())
            return cover_path

        external_cover_path = os.path.join(os.path.dirname(epub_path), 'cover.jpg')
        if os.path.exists(external_cover_path):
            shutil.copy(external_cover_path, cover_path)
            return cover_path

        logging.info(f"No cover found for {epub_path}, using default cover")
        return os.path.join(COVER_DIR, 'default.jpg')
    
    except (EpubException, KeyError, AttributeError, BadZipFile, IndexError, TypeError) as e:
        logging.error(f"Error getting cover {epub_path}: {str(e)}")
        return os.path.join(COVER_DIR, 'default.jpg')
    
def process_book(epub_file):
    logging.info(f"Processing book: {epub_file}")

    existing_ebook = Ebook.query.filter_by(epub_path=epub_file).first()
    if existing_ebook:
        logging.info(f"Skipping: {existing_ebook.title} by {existing_ebook.author} (already exists)")
        return None

    title, author_name, description, language, genre = extract_metadata(epub_file)
    if not title or not author_name:
        logging.error(f"Invalid title or author for {epub_file}")
        return None

    ebook = Ebook(title=title, author=author_name, description=description, language=language, genre=genre, epub_path=epub_file)
    logging.info(f"Created {ebook.title}")
    db.session.add(ebook)

    try:
        db.session.commit()
    except Exception as e:
        logging.error(f"Error committing {ebook.title}: {str(e)}")
        db.session.rollback()
        return None

    cover_path = extract_cover(epub_file, ebook.id)
    ebook.cover_path = cover_path

    try:
        db.session.commit()
    except Exception as e:
        logging.error(f"Error updating cover path for {ebook.title}: {str(e)}")
        db.session.rollback()

    return ebook

def process_book_with_context(epub_file):
    with app.app_context():
        process_book(epub_file)

def populate_database():
    with app.app_context():
        epub_files = []
        logging.info(f"Scanning directory: {EBOOK_DIR}")
        for author in os.listdir(EBOOK_DIR):
            author_path = os.path.join(EBOOK_DIR, author)
            if os.path.isdir(author_path):
                for book_title in os.listdir(author_path):
                    book_path = os.path.join(author_path, book_title)
                    if os.path.isdir(book_path):
                        for epub in os.listdir(book_path):
                            if epub.endswith(".epub"):
                                epub_file = os.path.join(book_path, epub)
                                epub_files.append(epub_file)
        if not epub_files:
            logging.warning("No EPUB file found")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_book_with_context, epub_file) for epub_file in epub_files]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in thread: {str(e)}")

        logging.info("Finished processing all books.")

                                        

if __name__ == '__main__':
    logging.info("Starting ebook import process...")
    populate_database()
    logging.info("Ebook import process completed")
