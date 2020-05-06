from contextlib import asynccontextmanager

import aioredis


class Redis:
    pool: aioredis.Redis = None

    @classmethod
    async def init(cls, redis_uri):
        cls.pool = await aioredis.create_redis_pool(redis_uri)

    @classmethod
    async def close(cls):
        cls.pool.close()
        await cls.pool.wait_closed()

    @classmethod
    @asynccontextmanager
    async def transaction(cls):
        assert cls.pool is not None
        transaction = cls.pool.multi_exec()

        try:
            yield transaction
        finally:
            await transaction.execute()


async def send_to_cache(page_id, label):
    assert Redis.pool is not None
    async with Redis.transaction() as transaction:
        transaction.sadd("all_labels", label)
        transaction.hincrby(label, page_id)


async def get_from_cache():
    assert Redis.pool is not None

    all_labels = await Redis.pool.smembers("all_labels")
    for label in all_labels:
        label = label.decode()

        async with Redis.transaction() as transaction:
            ids_to_counters = transaction.hgetall(label)
            transaction.srem("all_labels", label)
            transaction.delete(label)

        ids_to_counters = await ids_to_counters
        yield label, ids_to_counters
