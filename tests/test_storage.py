import asyncio
from datetime import timedelta

import aioredis
import attr
import pytest
import ujson

from com_redis_session import MissingSessionID

from ._utils import Session, SessionFactory, make_session_storage


async def test__find__deserialize_and_return(
    com_redis_client: aioredis.Redis,
) -> None:
    expected_session: Session = SessionFactory.build()
    await com_redis_client.set(
        expected_session.id,
        ujson.dumps(attr.asdict(expected_session)),
    )

    session_storage = make_session_storage(com_redis_client)
    session = await session_storage.find(expected_session.id)

    assert session == expected_session


async def test__find__missing_key_raise_exception(
    com_redis_client: aioredis.Redis,
) -> None:
    session_storage = make_session_storage(com_redis_client)

    with pytest.raises(MissingSessionID):
        await session_storage.find("missing_session_id")


async def test__add__insert_ok(com_redis_client: aioredis.Redis) -> None:
    session_storage = make_session_storage(com_redis_client)

    session: Session = SessionFactory.build()
    await session_storage.add(session)

    assert await session_storage.find(session.id) == session


async def test__add__override_ok(com_redis_client: aioredis.Redis) -> None:
    session_storage = make_session_storage(com_redis_client)

    previous: Session = SessionFactory.build()
    current: Session = SessionFactory.build(id=previous.id)

    await session_storage.add(previous)
    await session_storage.add(current)

    assert await session_storage.find(previous.id) == current


async def test__add__with_expired(com_redis_client: aioredis.Redis) -> None:
    session_storage = make_session_storage(
        com_redis_client,
        expire_after=timedelta(seconds=1),
    )
    session: Session = SessionFactory.build()

    await session_storage.add(session)
    await asyncio.sleep(1.5)

    with pytest.raises(MissingSessionID):
        await session_storage.find(session.id)


async def test__remove__exists_key(com_redis_client: aioredis.Redis) -> None:
    session_storage = make_session_storage(com_redis_client)
    session: Session = SessionFactory.build()
    await session_storage.add(session)

    await session_storage.remove(session)

    with pytest.raises(MissingSessionID):
        await session_storage.find(session.id)


async def test__remove__missing_id_ok(
    com_redis_client: aioredis.Redis,
) -> None:
    session_storage = make_session_storage(com_redis_client)
    session: Session = SessionFactory.build()
    await session_storage.add(session)

    await session_storage.remove(session)
    await session_storage.remove(session)

    with pytest.raises(MissingSessionID):
        await session_storage.find(session.id)
