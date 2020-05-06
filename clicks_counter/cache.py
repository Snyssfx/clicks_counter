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


async def send_to_cache(page_id, label):
    assert Redis.pool is not None

    await Redis.pool.sadd("all_labels", label)
    await Redis.pool.hincrby(label, page_id)


async def get_from_cache():
    assert Redis.pool is not None

    all_labels = await Redis.pool.smembers("all_labels")
    for label in all_labels:
        label = label.decode()

        transaction = Redis.pool.multi_exec()

        ids_to_counters = transaction.hgetall(label)
        transaction.srem("all_labels", label)
        transaction.delete(label)

        await transaction.execute()
        ids_to_counters = await ids_to_counters

        yield label, ids_to_counters
