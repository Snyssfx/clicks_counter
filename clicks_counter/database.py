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
            loop=asyncio.get_running_loop()
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


async def update_db():
    while True:
        await asyncio.sleep(DB_UPDATE_SEC)
        async for label, ids_to_counters in get_from_cache():
            with MySQL.get_cur() as cur:
                await _insert_or_update(cur, label, ids_to_counters)


async def _insert_or_update(cursor: aiomysql.Cursor, label, page_id_to_counter):
    values = []
    for page_id, counter in page_id_to_counter:
        page_id, counter = page_id.decode(), counter.decode()
        values.append((page_id, label, counter))

    await cursor.execute(
        f"REPLACE INTO clicks (page_id, label, counter) VALUES (?, ?, ?)",
        values
    )
