import connexion
import six

from swagger_server.models.borrow_request import BorrowRequest  # noqa: E501
from swagger_server.models.loan import Loan  # noqa: E501
from swagger_server import util


def api_loans_borrow_post(body):  # noqa: E501
    """Borrow a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = BorrowRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def api_loans_get(user_id=None, active=None):  # noqa: E501
    """List all loans

     # noqa: E501

    :param user_id: 
    :type user_id: int
    :param active: 
    :type active: str

    :rtype: List[Loan]
    """
    return 'do some magic!'


def api_loans_loan_id_get(loan_id):  # noqa: E501
    """Get loan by ID

     # noqa: E501

    :param loan_id: Unique loan identifier
    :type loan_id: int

    :rtype: Loan
    """
    return 'do some magic!'


def api_loans_loan_id_return_post(loan_id):  # noqa: E501
    """Return a book

     # noqa: E501

    :param loan_id: Unique loan identifier
    :type loan_id: int

    :rtype: None
    """
    return 'do some magic!'
