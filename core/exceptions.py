from rest_framework import status
from rest_framework.exceptions import APIException


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Incorrect authentication credentials."
    default_code = "authentication_failed"
