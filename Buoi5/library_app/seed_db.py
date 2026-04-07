import os
import time
from app import app, db
from models import Book

def seed_1_million_books():
    print(f"[*] Starting seed database script...")
    start_time = time.time()
    
    with app.app_context():
        # Check current count
        current_count = Book.query.count()
        if current_count >= 1000000:
            print(f"[*] Database already has {current_count} books. Aborting seed to prevent duplication.")
            return

        print("[*] Generating 1,000,000 mock book records. This will take a moment...")
        
        batch_size = 100000
        total_books = 1000000
        
        for i in range(0, total_books, batch_size):
            batch_start_time = time.time()
            books_batch = []
            for j in range(i, i + batch_size):
                books_batch.append({
                    "title": f"Book Title {j}",
                    "author": f"Author {j % 1000}", # 1000 unique authors
                    "category": f"Category {j % 10}", # 10 unique categories
                    "available_copies": (j % 5) + 1
                })
            
            db.session.bulk_insert_mappings(Book, books_batch)
            db.session.commit()
            
            batch_duration = time.time() - batch_start_time
            print(f"[-] Inserted batch {i} to {i + batch_size - 1} in {batch_duration:.2f} seconds...")
            
    total_time = time.time() - start_time
    print(f"\n[*] Successfully seeded 1,000,000 books in {total_time:.2f} seconds!")

if __name__ == "__main__":
    seed_1_million_books()
