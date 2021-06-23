from datetime import timedelta
from typing import Callable, Generic, Optional, Protocol, TypeVar

import aioredis
import attr

from .exceptions import MissingSessionID


class Entity(Protocol):
    id: str


_SessionT = TypeVar("_SessionT", bound=Entity)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class RedisSessionStorage(Generic[_SessionT]):
    _redis: aioredis.Redis
    _expire_after: Optional[timedelta] = None
    _dumps: Callable[[_SessionT], str] = attr.ib(kw_only=True)
    _loads: Callable[[str], _SessionT] = attr.ib(kw_only=True)

    async def find(self, session_id: str) -> _SessionT:
        string_view = await self._redis.get(session_id)
        if string_view is None:
            raise MissingSessionID

        return self._loads(string_view)

    async def add(
        self,
        session: _SessionT,
    ) -> None:
        await self._redis.set(
            session.id,
            self._dumps(session),
            expire=self._calculate_expire(),
        )

    async def remove(self, session: _SessionT) -> None:
        await self._redis.delete(session.id)

    def _calculate_expire(self) -> int:
        return (
            self._expire_after.seconds
            if self._expire_after is not None
            else 0
        )
