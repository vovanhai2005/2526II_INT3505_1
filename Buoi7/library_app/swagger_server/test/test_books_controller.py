# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.book_create import BookCreate  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_api_books_book_id_delete(self):
        """Test case for api_books_book_id_delete

        Delete a book
        """
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_get(self):
        """Test case for api_books_book_id_get

        Get book by ID
        """
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_put(self):
        """Test case for api_books_book_id_put

        Update a book
        """
        body = BookCreate()
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_book(self):
        """Test case for create_book

        Create a new book
        """
        body = BookCreate()
        response = self.client.open(
            '/api/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_books(self):
        """Test case for get_books

        List all books
        """
        query_string = [('category', 'category_example'),
                        ('author', 'author_example')]
        response = self.client.open(
            '/api/books',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
