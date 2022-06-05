import json
import os
from datetime import datetime, timezone, timedelta

import jwt
from typing import Union, Callable, Optional
from django.http import HttpResponse, HttpRequest, FileResponse
from sqlalchemy import select, update, insert, delete
from sqlalchemy.engine import LegacyCursorResult
from sqlalchemy.sql.functions import now

from db.utils import Engine
from db.tables import SessionDB
from redis_cache.utils import redis_client


_jwt_key = open(os.environ['JWT_KEY_PATH'], "rb").read()


class AuthUserInfo:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.is_admin: bool = False


class AuthMiddleware:

    def __init__(self, get_response: Callable):
        self._get_response = get_response

    def __call__(self, request: HttpRequest) -> Union[HttpResponse, FileResponse]:
        user_info = AuthUserInfo()
        access_token = request.headers.get('access_token', None)
        refresh_token = request.headers.get('refresh_token', None)

        user_info.access_token = access_token
        user_info.refresh_token = refresh_token

        if access_token is not None:
            try:
                payload = jwt.decode(access_token, key=_jwt_key, algorithms='HS256')
            except jwt.ExpiredSignatureError:
                return HttpResponse(status=401, content="access_token expire")
            except jwt.InvalidTokenError:
                return HttpResponse(status=401, content="access_token invalid")

            try:
                user_info.user_id = int(payload.get('user_id', None))
            except TypeError:
                return HttpResponse(status=401, content="access_token invalid")

            secret = payload.get('secret', None)
            if redis_client.get(secret) is not None:
                return HttpResponse(status=401, content="access_token rejected")

        elif refresh_token is not None:
            try:
                payload = jwt.decode(refresh_token, key=_jwt_key, algorithms='HS256')
            except jwt.ExpiredSignatureError:
                return HttpResponse(status=401, content="access_token expire")
            except jwt.InvalidTokenError:
                return HttpResponse(status=401, content="access_token invalid")

            try:
                user_info.user_id = int(payload.get('user_id', None))
            except TypeError:
                return HttpResponse(status=401, content="access_token invalid")

            result: LegacyCursorResult = Engine.execute(
                select(SessionDB.c.session_id).where(
                    SessionDB.c.refresh_token == refresh_token,
                    SessionDB.c.user_id == user_info.user_id,
                )
            )
            if result.rowcount == 0:
                return HttpResponse(status=401, content="refresh_token rejected")
            Engine.execute(
                update(SessionDB.c.last_used_dttm)
                .where(SessionDB.c.refresh_token == refresh_token)
                .values({'last_used_dttm': now()})
            )

            return HttpResponse(json.dumps({
                'access_token': AuthMiddleware.make_access_token(refresh_token, user_info.user_id)}
            ))

        else:
            # TODO check here that such method could be invoked without permissions
            return HttpResponse(status=401, content="no token")

        request.user = user_info

        return self._get_response(request)

    @staticmethod
    def REFRESH_TOKEN_LIFETIME() -> timedelta:
        """Lifetime of new access tokens: 120 days."""
        return timedelta(days=120)

    @staticmethod
    def ACCESS_TOKEN_LIFETIME() -> timedelta:
        """Lifetime of new access tokens: 10 minutes."""
        return timedelta(minutes=10)

    @staticmethod
    def make_refresh_token(user_id: int) -> str:
        """
        Generate new refresh token for user.
        Lifetime of new token is taken from `AuthMiddleware.REFRESH_TOKEN_LIFETIME()`
        This function also updates database.

        :param user_id: int - user id
        :return: str - new access token for user
        """
        valid_till_dttm = datetime.now(tz=timezone.utc) + AuthMiddleware.REFRESH_TOKEN_LIFETIME()
        refresh_token = jwt.encode({'user_id': user_id, 'exp': valid_till_dttm}, key=_jwt_key)
        Engine.execute(
            insert(SessionDB).values({
                'user_id': user_id,
                'refresh_token': refresh_token,
                'valid_till_dttm': valid_till_dttm,
            })
        )
        return refresh_token

    @staticmethod
    def make_access_token(refresh_token: str, user_id: int) -> str:
        """
        Generate new access token for user.
        Lifetime of new token is taken from `AuthMiddleware.ACCESS_TOKEN_LIFETIME()`

        :param refresh_token: str
        :param user_id: int
        :return: str - new access token for user
        """
        valid_till_dttm = datetime.now(tz=timezone.utc) + AuthMiddleware.ACCESS_TOKEN_LIFETIME()
        access_token = jwt.encode({'user_id': user_id, 'exp': valid_till_dttm}, key=_jwt_key)

        # to access access_token by refresh
        redis_client.set(refresh_token, access_token)

        return access_token

    @staticmethod
    def reject_session(session_id: int) -> None:
        """
        Remove session from database and mark refresh and access tokens as rejected.
        For future requests such tokens will be invalid.

        :param session_id: int - session id in database
        :return: None
        """
        result: LegacyCursorResult = Engine.execute(
            select(SessionDB.c.refresh_token).where(SessionDB.s.session_id == session_id)
        )
        if result.rowcount == 0:
            return
        refresh_token = result.first()[0]

        access_token: Optional[bytes] = redis_client.get(refresh_token)
        if access_token is not None:
            redis_client.set(access_token.decode(), "0")

        Engine.execute(delete(SessionDB).where(SessionDB.s.session_id == session_id))
