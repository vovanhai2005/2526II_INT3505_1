import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.new_book import NewBook  # noqa: E501
from openapi_server import util


def add_book(body):  # noqa: E501
    """Add a new book

     # noqa: E501

    :param new_book: 
    :type new_book: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    new_book = body
    if connexion.request.is_json:
        new_book = NewBook.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_book(book_id):  # noqa: E501
    """Delete a book

     # noqa: E501

    :param book_id: ID of the book to delete
    :type book_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_book_by_id(book_id):  # noqa: E501
    """Get a book by its ID

     # noqa: E501

    :param book_id: ID of the book to retrieve
    :type book_id: int

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_books():  # noqa: E501
    """Get all books

     # noqa: E501


    :rtype: Union[List[Book], Tuple[List[Book], int], Tuple[List[Book], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_book(book_id, body):  # noqa: E501
    """Update an existing book

     # noqa: E501

    :param book_id: ID of the book to update
    :type book_id: int
    :param new_book: 
    :type new_book: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    new_book = body
    if connexion.request.is_json:
        new_book = NewBook.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
