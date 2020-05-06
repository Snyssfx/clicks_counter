# clicks_counter
The server waits for websocket connection from clients,
then get some statistical info,
e.g.: `{"id": 123, "label": "view"}`
and store it in database.

The server can be split to 2 parts:
1) websocket server, that store all info in cache (redis here)
2) coroutine that consume the info from redis and store
it in database (MySQL)


### Running
```
docker volume create mysql-data
docker-compose up -d
docker-compose exec mysql mysql -u root -p
```
(password 123)

Then execute all from
[migrations](./clicks_counter/migrations)

### Testing
After server running, type:
```
docker-compose exec server pytest
```

### Notes
* I am not MySQL expert, so unfortunately
the server connects to it as `root` user :(
* Also I have never created migrations for
asyncio and MySQL
