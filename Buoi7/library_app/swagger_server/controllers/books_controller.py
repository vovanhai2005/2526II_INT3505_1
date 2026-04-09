import connexion
import six

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.book_create import BookCreate  # noqa: E501
from swagger_server import util


def api_books_book_id_delete(book_id):  # noqa: E501
    """Delete a book

     # noqa: E501

    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: None
    """
    return 'do some magic!'


def api_books_book_id_get(book_id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: Book
    """
    return 'do some magic!'


def api_books_book_id_put(body, book_id):  # noqa: E501
    """Update a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: None
    """
    if connexion.request.is_json:
        body = BookCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def create_book(body):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = BookCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_books(category=None, author=None):  # noqa: E501
    """List all books

     # noqa: E501

    :param category: Filter by category
    :type category: str
    :param author: Filter by author
    :type author: str

    :rtype: List[Book]
    """
    return 'do some magic!'
