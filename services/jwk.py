import flask_restful
from flask import request
import jwt

__secret__ = 'ExcellentSecret'
__issuer__ = "FIREAPP2.0"

from domain import session_scope, User
from repository.volunteer_repository import get_roles_for_user


class JWKService:

    @staticmethod
    def generate(subject: int, name: str, role: str) -> str:
        """
        Generate a JWT token for communication between client and application server.
        :param subject: The subject (ID) of the client for the token.
        :param name: The name of the client for the token.
        :param role: The role of the client for the token.
        :return: The token as a string.
        """
        # TODO: Authentication
        #   - Add token expiry & refreshing, low priority in MVP
        token = jwt.encode({"sub": f"{subject}", "name": name, "role": role, "iss": __issuer__}, __secret__, algorithm="HS256")
        return token

    @staticmethod
    def validate(token) -> bool:
        try:
            decoded = jwt.decode(token, __secret__, algorithms=["HS256"])
        except Exception as e:
            return False
        return True

    @staticmethod
    def validate_admin(token) -> bool:
        try:
            decoded = jwt.decode(token, __secret__, algorithms=["HS256"])
            print(decoded.claims)
            # TODO: Validate is admin
        except Exception as e:
            return False
        return True

    @staticmethod
    def validate_role(token, valid_roles) -> bool:
        try:
            decoded = jwt.decode(token, __secret__, algorithms=["HS256"])
            role = decoded.get("role")
            for roles in valid_roles:
                if role == roles.name:
                    return True
        except Exception as e:
            pass
        return False


def requires_auth(func):
    jwkservice = JWKService()

    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if authorization_header is None:
            # TODO: Throw an error
            pass
        token = authorization_header[len('Bearer '):]
        if jwkservice.validate(token):
            return func(*args, **kwargs)
        return flask_restful.abort(401)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def requires_admin(func):
    jwkservice = JWKService()

    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if authorization_header is None:
            pass
        token = authorization_header[len('Bearer '):]
        if jwkservice.validate_admin(token):
            return func(*args, **kwargs)
        return flask_restful.abort(401)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def has_role(*roles):
    def decorator(func):
        jwkservice = JWKService()

        def wrapper(*args, **kwargs):
            print(**kwargs)
            print(kwargs)
            print(*args)
            print(args[0].__dict__)
            authorization_header = request.headers.get("Authorization")
            if authorization_header is None:
                pass
            token = authorization_header[len('Bearer '):]
            if jwkservice.validate(token) and jwkservice.validate_role(token, roles):
                return func(*args, **kwargs)
            return flask_restful.abort(401)

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper

    return decorator