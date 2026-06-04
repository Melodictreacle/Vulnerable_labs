# Redis Post Exploitation Due to Master and Slave Synchronisation

[中文版本(Chinese version)](README.zh-cn.md)

Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker.

Redis which version starts from 4.0, prior to 5.0.5, can be exploit through the synchronisation between master and slave by an authenticated visitor.

Reference:

- <https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf>

## Vulnerability Environment

Execute following command to start a Redis server 4.0.14:

```
docker compose up -d
```

After server is started, you can connect to this server without credentials by `redis-cli`:

```
redis-cli -h your-ip
```

## Exploit

Use [this script](https://github.com/vulhub/redis-rogue-getshell) to execute arbitrary commands:

![](1.png)
```

## Exploit

Use [this script](https://github.com/vulhub/redis-rogue-getshell) to execute arbitrary commands:

![](1.png)

## Status Checker Client (client2.py)

A benign status checker client is also provided as `client2.py`.

### Description
Redis Normal User Client
A benign client to connect to a Redis database using standard socket protocol,
and retrieve basic status information and set/get test keys.

### Usage
```bash
python3 client2.py [--mode {check,active}] [--port PORT] <target>
```

### Parameters
* `target`: Target Redis host (IP or hostname)
* `--port PORT`: Target Redis port (default: `6379`)
* `--mode {check,active}`: Simulation mode. `check` connects and sends PING/INFO (default); `active` performs standard benign key operations (`SET`, `GET`, `DEL`).

