class RedisSessionStorageException(Exception):
    pass


class MissingSessionID(RedisSessionStorageException):
    pass
