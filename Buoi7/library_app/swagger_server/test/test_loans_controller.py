# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.borrow_request import BorrowRequest  # noqa: E501
from swagger_server.models.loan import Loan  # noqa: E501
from swagger_server.test import BaseTestCase


class TestLoansController(BaseTestCase):
    """LoansController integration test stubs"""

    def test_api_loans_borrow_post(self):
        """Test case for api_loans_borrow_post

        Borrow a book
        """
        body = BorrowRequest()
        response = self.client.open(
            '/api/loans/borrow',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_loans_get(self):
        """Test case for api_loans_get

        List all loans
        """
        query_string = [('user_id', 56),
                        ('active', 'active_example')]
        response = self.client.open(
            '/api/loans',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_loans_loan_id_get(self):
        """Test case for api_loans_loan_id_get

        Get loan by ID
        """
        response = self.client.open(
            '/api/loans/{loan_id}'.format(loan_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_loans_loan_id_return_post(self):
        """Test case for api_loans_loan_id_return_post

        Return a book
        """
        response = self.client.open(
            '/api/loans/{loan_id}/return'.format(loan_id=56),
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
