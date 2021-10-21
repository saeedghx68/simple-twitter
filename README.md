Simple-Twitter
=============
A simple twitter is an application which enables users to register, post tweets and search by tag.
Simple Twitter is written in [sanic](https://github.com/huge-success/sanic) which uses [uvloop](https://github.com/magicstack/uvloop) in order to have async call.

In this project I used these technologies:

* `python` version: `3.10.0`
* `PostgreSQL` (to store tweets)
* `redis` (to cache tag and related tweets)
* `Sanic` (as an asynchronous web API)

`Sanic` and `uvloop` makes `asyncio` fast. In fact, it is at least 2x faster than `NodeJs`, `gevent`, as well as any other Python asynchronous frameworks. The performance of `uvloop-based` `asyncio` is close to that of `Go` programs. 
 
Run
-----------
clone the project and run with docker

```bash
cp .env.tpl .env
docker-compose build
docker-compose up -d # it will be exposed on port 2080
```


After this, you can work with `API` by `Swagger`. You can see swagger via <http://127.0.0.1:2080/swagger> url.
 


Run tests
-----------
```bash
docker exec -it [API DOCKER NAME] ENVIRONMENT=test pytest unittesting/
```

-----------
**Test and Build**

to run test or build application, we have `make` commands. So, to run tests:

**Note:** please install `python3.10` before run **`make`** command


**To test application**
```bash
make test
```


**Run app**
```
make all
```
This command will install `python3-pip` and `virtualenv`.
After that run it creates `virtualenv` and activates it.Then it installs requirements packages, and Finally run the following command:
`python -m sanic server.app --host=${host} --port=${port} --workers=${worker_count}`

for example:
```
python -m sanic server.app --host=0.0.0.0 --port=2080 --workers=12
``` 

Why use redis?
-------------
**Note**:
I choosed `redis` to cache tweets and tags. At the first, Simple twitter looks up for tweets when you search by tag on `redis`, If searched tag does not exist, it searches in `pg` and after that it inserts all related messages into `redis` to have them cached.
I want to say, if the project grows up, you have to implement logic to store important tags and messages on some cache engine such as `redis`. 


Why `asyncio` and `sanic` and `uvloop`?
------------
**asyncio & uvloop**

The asyncio module, introduced by PEP 3156, is a collection of network transports, protocols, and streams abstractions, with a pluggable event loop. The event loop is the heart of asyncio. It provides APIs for:

    * scheduling calls,
    * transmitting data over the network,
    * performing DNS queries,
    * handling OS signals,
    * convenient abstractions to create servers and connections,
    * working with subprocesses asynchronously.
    
when you should consider sanic?
    
    * high throughput
    * micorservices
    * smaller web apps
    * it was super easy to get started

**Architecture**

uvloop is written in Cython and is built on top of libuv.

libuv is a high performance, multiplatform asynchronous I/O library used by nodejs. Because of how wide-spread and popular nodejs is, libuv is fast and stable.

uvloop implements all asyncio event loop APIs. High-level Python objects wrap low-level libuv structs and functions. Inheritance is used to keep the code DRY and ensure that any manual memory management is in sync with libuv primitives' lifespans.

It is safe to conclude that, with uvloop, it is possible to write Python networking code that can push tens of thousands of requests per second per CPU core. On multicore systems a process pool can be used to scale the performance even further.

uvloop and asyncio, combined with the power of async/await in Python 3.5+ , makes it easier than ever to write high-performance networking code in Python.


**[references](https://magic.io/blog/uvloop-blazing-fast-python-networking/)**