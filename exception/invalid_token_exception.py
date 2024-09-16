from .fireapp_exception import FireAppException


class InvalidTokenError(FireAppException):
    """
    A custom exception used to handle invalid tokens for the user.
    """
    def __init__(self, message='Invalid token for the user'):
        self.message = message
        super().__init__(self.message)
