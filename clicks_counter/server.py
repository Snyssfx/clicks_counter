import json
import asyncio
import logging
from signal import SIGINT, SIGTERM

from websockets.server import Serve

from clicks_counter.cache import Redis
from clicks_counter.database import update_db, MySQL, update_db_loop

import cerberus as cerberus
import websockets

from clicks_counter.cache import send_to_cache


def create_server(host, port):
    return websockets.serve(on_client_connect, host, port)


async def main(
        server: Serve,
        db_host,
        db_port,
        db_user,
        db_password,
        db_name,
        redis_uri,
        db_update_sec,
):
    logging.basicConfig(level=logging.INFO)

    try:
        await MySQL.init(db_host, db_port, db_user, db_password, db_name)
        await Redis.init(redis_uri)
        await update_db()

        update_task = asyncio.create_task(update_db_loop(db_update_sec))

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(SIGINT, server.ws_server.close)
        loop.add_signal_handler(SIGTERM, server.ws_server.close)

        await server
        await server.ws_server.wait_closed()
        update_task.cancel()

    finally:
        await update_db()
        await Redis.close()
        await MySQL.close()


async def on_client_connect(websocket: websockets.WebSocketServerProtocol, path):
    validator = cerberus.Validator({
        "id": {"required": True, "type": "integer"},
        "label": {"required": True, "type": "string"},
    })

    logging.info(f"connection started! {path}")
    async for msg in websocket:
        msg = json.loads(msg)
        if not validator.validate(msg):
            raise Exception("Invalid data!")

        await send_to_cache(msg["id"], msg["label"])

    logging.info(f"connection closed! {path}")
