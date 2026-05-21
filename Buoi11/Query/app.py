from flask import Flask, request, jsonify

app = Flask(__name__)

# Dữ liệu tĩnh giả lập Database - Cửa hàng sách
books = [
    {"id": 1, "title": "Clean Code",            "genre": "technology",  "author": "Robert C. Martin", "price": 35.99},
    {"id": 2, "title": "The Pragmatic Programmer","genre": "technology", "author": "David Thomas",      "price": 42.50},
    {"id": 3, "title": "Dune",                   "genre": "sci-fi",      "author": "Frank Herbert",     "price": 18.00},
    {"id": 4, "title": "Foundation",             "genre": "sci-fi",      "author": "Isaac Asimov",      "price": 15.75},
    {"id": 5, "title": "Sapiens",                "genre": "non-fiction", "author": "Yuval Noah Harari", "price": 22.00},
    {"id": 6, "title": "Atomic Habits",          "genre": "non-fiction", "author": "James Clear",       "price": 19.99},
    {"id": 7, "title": "The Hobbit",             "genre": "fantasy",     "author": "J.R.R. Tolkien",    "price": 14.50},
    {"id": 8, "title": "1984",                   "genre": "sci-fi",      "author": "George Orwell",     "price": 12.99},
]

@app.route('/books', methods=['GET'])
def search_books():
    # Nhận các tham số Query (Query Parameters) từ URL
    genre     = request.args.get('genre')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by   = request.args.get('sort')
    limit     = request.args.get('limit', type=int)

    result = books

    # Lọc (Filtering) - Lọc theo thể loại
    if genre:
        result = [b for b in result if b['genre'] == genre]

    # Lọc (Filtering) - Lọc theo giá
    if min_price is not None:
        result = [b for b in result if float(b['price']) >= min_price]
    if max_price is not None:
        result = [b for b in result if float(b['price']) <= max_price]

    # Sắp xếp (Sorting)
    if sort_by == 'price_asc':
        result = sorted(result, key=lambda x: x['price'])
    elif sort_by == 'price_desc':
        result = sorted(result, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'title_asc':
        result = sorted(result, key=lambda x: x['title'])

    # Phân trang/Giới hạn (Pagination/Limit)
    if limit:
        result = result[:limit]

    return jsonify({
        "metadata": {
            "total_matches": len(result),
            "filters_applied": {
                "genre":     genre,
                "min_price": min_price,
                "max_price": max_price,
                "sort":      sort_by,
                "limit":     limit
            }
        },
        "data": result
    }), 200

if __name__ == '__main__':
    print("Starting Bookstore Query API on port 5003...")
    app.run(port=5003)
