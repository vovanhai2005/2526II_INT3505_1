import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server.models.user_create import UserCreate  # noqa: E501
from swagger_server import util


def create_user(body):  # noqa: E501
    """Create a new user

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = UserCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_user(user_id):  # noqa: E501
    """Delete a user

     # noqa: E501

    :param user_id: Unique user identifier
    :type user_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_user(user_id):  # noqa: E501
    """Get a user by ID

     # noqa: E501

    :param user_id: Unique user identifier
    :type user_id: int

    :rtype: User
    """
    return 'do some magic!'


def get_users():  # noqa: E501
    """List all users

     # noqa: E501


    :rtype: List[User]
    """
    return 'do some magic!'


def update_user(body, user_id):  # noqa: E501
    """Update a user

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param user_id: Unique user identifier
    :type user_id: int

    :rtype: None
    """
    if connexion.request.is_json:
        body = UserCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
