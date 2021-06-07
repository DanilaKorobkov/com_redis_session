import secrets
from datetime import timedelta

import aioredis
import attr
import factory
from marshmallow import Schema, fields, post_load

from com_redis_session import Entity, RedisSessionStorage


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Session(Entity):
    id: str
    access_token: str
    refresh_token: str


class SessionSchema(Schema):
    id = fields.Str(required=True)
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)

    @post_load
    def release(  # pylint: disable=no-self-use
        self,
        data: dict,
        **_,
    ) -> Session:
        return Session(**data)


class SessionFactory(factory.Factory):

    class Meta:
        model = Session

    id = factory.LazyFunction(secrets.token_urlsafe)
    access_token = factory.LazyFunction(secrets.token_urlsafe)
    refresh_token = factory.LazyFunction(secrets.token_urlsafe)


def make_session_storage(
    redis: aioredis.Redis,
    expire_after: timedelta = None,
) -> RedisSessionStorage[Session]:
    schema = SessionSchema()
    return RedisSessionStorage[Session](
        redis,
        expire_after=expire_after,
        dumps=schema.dumps,
        loads=schema.loads,
    )
