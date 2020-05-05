import asyncio
from signal import SIGINT, SIGTERM

import websockets

from clicks_counter.cache import Redis
from clicks_counter.database import update_db, MySQL
from clicks_counter.server import on_client_connect
from clicks_counter.settings import HOST, PORT, DB_HOST, DB_PORT, DB_USER, \
    DB_PASSWORD, REDIS_URI, DB


async def main():
    try:
        await MySQL.init(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB)
        await Redis.init(REDIS_URI)

        asyncio.create_task(update_db())
        server = websockets.serve(on_client_connect, HOST, PORT)

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(SIGINT, server.ws_server.close)
        loop.add_signal_handler(SIGTERM, server.ws_server.close)

        await server
        await server.ws_server.wait_closed()

    finally:
        await Redis.close()
        await MySQL.close()


if __name__ == '__main__':
    asyncio.run(main())
