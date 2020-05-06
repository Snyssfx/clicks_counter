import asyncio
from contextlib import asynccontextmanager

import aiomysql

from clicks_counter.cache import get_from_cache
from clicks_counter.settings import DB_UPDATE_SEC


class MySQL:
    pool: aiomysql.Pool = None

    @classmethod
    async def init(cls, host, port, user, password, db):
        cls.pool = await aiomysql.create_pool(
            host=host, port=port, user=user, password=password, db=db,
            loop=asyncio.get_running_loop(),
        )

    @classmethod
    async def close(cls):
        cls.pool.close()
        await cls.pool.wait_closed()

    @classmethod
    @asynccontextmanager
    async def get_cur(cls) -> aiomysql.Cursor:
        assert cls.pool is not None

        async with cls.pool.acquire() as conn:
            async with conn.cursor() as cur:
                yield cur

            await conn.commit()


async def update_db(db_update_sec):
    while True:
        await asyncio.sleep(db_update_sec)
        async for label, ids_to_counters in get_from_cache():
            async with MySQL.get_cur() as cur:
                await _insert_or_update(cur, label, ids_to_counters)


async def _insert_or_update(cursor: aiomysql.Cursor, label, page_id_to_counter):
    values = []
    for page_id, counter in page_id_to_counter.items():
        page_id, counter = page_id.decode(), counter.decode()
        values.append((int(page_id), label, int(counter), int(counter)))

    await cursor.executemany(
        f"INSERT INTO clicks "
        f"SET page_id = %s, label = %s, counter = %s"
        f" ON DUPLICATE KEY UPDATE counter = counter + %s",
        values
    )
