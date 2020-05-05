import asyncio
import json

import aiomysql
import pytest
import websockets

from clicks_counter.database import MySQL
from clicks_counter.settings import PORT, DB_UPDATE_SEC, DB_HOST, DB_PORT, \
    DB_USER, DB_PASSWORD, DB
from main import main

messages = [
    {"id": 1, "label": "view"},
    {"id": 1, "label": "click"},

    {"id": 1, "label": "view"},
    {"id": 1, "label": "click"},

    {"id": 2, "label": "view"},
    {"id": 2, "label": "click"},
]

# page_id, label, counter
result = {
    (1, "view", 2),
    (1, "click", 2),
    (2, "view", 1),
    (2, "click", 1),
}


@pytest.mark.asyncio
async def test_client():
    db_host, db_port, db_user, db_pass, db_name, host, port, redis_uri = (
        "mysql", 3306, "root", "123", "test", "127.0.0.1", 1235, "redis://redis:6379/1"
    )

    asyncio.create_task(main(
        db_host, db_port, db_user, db_pass, db_name, host, port, redis_uri
    ))
    await asyncio.sleep(1)

    async with websockets.connect(f"ws://{host}:{port}") as connection:
        for msg in messages:
            msg = json.dumps(msg)
            await connection.send(msg)

    await asyncio.sleep(DB_UPDATE_SEC + 1)
    await MySQL.init(db_host, db_port, db_user, db_pass, db_name)
    async with MySQL.get_cur() as cur:
        await cur.execute(f"SELECT * FROM clicks")
        r = cur.fetchall().result()
        assert set(r) == result
