import json
import logging

import cerberus as cerberus
import websockets

from clicks_counter.cache import send_to_cache


async def on_client_connect(
        websocket: websockets.WebSocketServerProtocol, path: str
):
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
