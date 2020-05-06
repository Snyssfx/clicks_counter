import asyncio
import json
import os

import pytest
import websockets

from clicks_counter.cache import Redis
from clicks_counter.database import MySQL
from main import main

messages = [
    {"id": 1, "label": "view"},
    {"id": 1, "label": "click"},

    {"id": 1, "label": "view"},
    {"id": 1, "label": "click"},

    {"id": 2, "label": "view"},
    {"id": 2, "label": "click"},
]


def get_result(n_messages):
    # page_id, label, counter
    return {
        (1, "view", 2 * n_messages),
        (1, "click", 2 * n_messages),
        (2, "view", 1 * n_messages),
        (2, "click", 1 * n_messages),
    }


# server settings
db_host = "mysql"
db_port = 3306
db_user = "root"
db_pass = "123"
db_name = "test"
host = "127.0.0.1"
port = 1235
redis_uri = "redis://redis:6379/1"
db_update_sec = 0.5


@pytest.fixture()
async def server():
    await MySQL.init(db_host, db_port, db_user, db_pass, db_name)
    async with MySQL.get_cur() as cur:
        await cur.execute(f"DELETE from clicks")

    asyncio.create_task(main(
        db_host,
        db_port,
        db_user,
        db_pass,
        db_name,
        host,
        port,
        redis_uri,
        db_update_sec,
    ))
    await asyncio.sleep(db_update_sec)

    yield

    await MySQL.close()


async def send_messages():
    async with websockets.connect(f"ws://{host}:{port}") as connection:
        for msg in messages:
            msg = json.dumps(msg)
            await connection.send(msg)


@pytest.mark.asyncio
async def test_client(server):
    await send_messages()
    await asyncio.sleep(db_update_sec + 1)
    async with MySQL.get_cur() as cur:
        await cur.execute(f"SELECT * FROM clicks")
        r = cur.fetchall().result()
        assert set(r) == get_result(n_messages=1)


@pytest.mark.asyncio
async def test_redis_is_empty(server):
    await send_messages()
    await asyncio.sleep(db_update_sec + 1)

    breakpoint()
    all_keys = await Redis.pool.keys("*")
    assert all_keys == []

    await send_messages()
    await asyncio.sleep(db_update_sec + 1)

    async with MySQL.get_cur() as cur:
        await cur.execute(f"SELECT * FROM clicks")
        r = cur.fetchall().result()
        assert set(r) == get_result(n_messages=2)
