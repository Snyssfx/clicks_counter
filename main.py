import asyncio

from clicks_counter.server import main, create_server
from clicks_counter.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB, \
    HOST, PORT, REDIS_URI, DB_UPDATE_SEC


async def run():
    server = create_server(HOST, PORT)

    await main(
        server=server,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        db_name=DB,
        redis_uri=REDIS_URI,
        db_update_sec=DB_UPDATE_SEC,
    )


if __name__ == '__main__':
    asyncio.run(run())
