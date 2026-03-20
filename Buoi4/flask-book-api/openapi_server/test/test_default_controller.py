import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.new_book import NewBook  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_book(self):
        """Test case for add_book

        Add a new book
        """
        new_book = {"author":"author","title":"title"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/books',
            method='POST',
            headers=headers,
            data=json.dumps(new_book),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_book(self):
        """Test case for delete_book

        Delete a book
        """
        headers = { 
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_book_by_id(self):
        """Test case for get_book_by_id

        Get a book by its ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_books(self):
        """Test case for get_books

        Get all books
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/books',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_book(self):
        """Test case for update_book

        Update an existing book
        """
        new_book = {"author":"author","title":"title"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(new_book),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
