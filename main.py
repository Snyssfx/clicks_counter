import asyncio
import logging
from signal import SIGINT, SIGTERM

import websockets

from clicks_counter.cache import Redis
from clicks_counter.database import update_db, MySQL
from clicks_counter.server import on_client_connect
from clicks_counter.settings import HOST, PORT, DB_HOST, DB_PORT, DB_USER, \
    DB_PASSWORD, REDIS_URI, DB, DB_UPDATE_SEC


async def main(
        db_host,
        db_port,
        db_user,
        db_password,
        db_name,
        host,
        port,
        redis_uri,
        db_update_sec,
):
    logging.basicConfig(level=logging.INFO)

    try:
        await MySQL.init(db_host, db_port, db_user, db_password, db_name)
        await Redis.init(redis_uri)

        asyncio.create_task(update_db(db_update_sec))
        server = websockets.serve(on_client_connect, host, port)

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(SIGINT, server.ws_server.close)
        loop.add_signal_handler(SIGTERM, server.ws_server.close)

        await server
        await server.ws_server.wait_closed()

        await update_db(0)

    finally:
        await Redis.close()
        await MySQL.close()


if __name__ == '__main__':
    asyncio.run(main(
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        db_name=DB,
        host=HOST,
        port=PORT,
        redis_uri=REDIS_URI,
        db_update_sec=DB_UPDATE_SEC,
    ))
