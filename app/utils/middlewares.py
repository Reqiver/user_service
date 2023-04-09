from starlette.authentication import AuthCredentials, AuthenticationError, BaseUser
from starlette.requests import HTTPConnection
from typing import Tuple

from jose import JWTError
from starlette.types import Scope, Receive, Send

from app.utils.user_utils import get_current_user


class CustomUser(BaseUser):
    """ Sample API User that gives basic functionality """

    def __init__(
            self,
            first_name: str = None,
            last_name: str = None,
            user_id: str = None,
            role: str = None,
    ):
        """ FastAPIUser Constructor
        Args:
            first_name (str): The first name of the user
            last_name (str): The last name of the user
            user_id (str): The user id
            role (str): The user role
        """
        self.first_name = first_name
        self.last_name = last_name
        self.id = user_id
        self.role = role

    @property
    def is_authenticated(self) -> bool:
        """ Checks if the user is authenticated.
        Returns:
            bool: True if the user is authenticated
        """
        return self.id is not None

    @property
    def display_name(self) -> str:
        """ Display name of the user """
        return f'{self.first_name} {self.last_name}'

    @property
    def identity(self) -> str:
        """ Identification attribute of the user """
        return self.id


class JWTAuthenticationMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(
            self,
            scope: Scope,
            receive: Receive,
            send: Send,
    ):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        connection = HTTPConnection(scope)

        scope["auth"], scope["user"] = await self.authenticate(connection)
        await self.app(scope, receive, send)

    @staticmethod
    async def get_user(token: str):
        """ Method for getting the user is passed.

        Args:
            token (str): A JWT token
        Returns:
            CustomUser: A CustomUser instance with basic attributes
        """
        try:
            user = await get_current_user(token)
            return CustomUser(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
            )
        except JWTError:
            raise AuthenticationError("Invalid token")

    async def authenticate(self, conn: HTTPConnection) -> Tuple[AuthCredentials, BaseUser]:
        """
        The authenticate method is invoked each time a route is called
        that the middleware is applied to.

        Args:
            conn (HTTPConnection): An HTTP connection of FastAPI/Starlette
        Returns:
            Tuple[AuthCredentials, BaseUser]: A tuple of AuthCredentials (scopes) and a user object
            that is or inherits from BaseUser
        """

        try:
            token = self.get_token_from_header(conn.headers["Authorization"])
        except KeyError:
            return AuthCredentials(scopes=[]), CustomUser()

        user = await self.get_user(token)

        return AuthCredentials(scopes=['authenticated', user.role]), user

    @staticmethod
    def get_token_from_header(authorization_header: str):
        scheme, token = authorization_header.split()
        if scheme.lower() == "bearer":
            return token
        raise KeyError()
