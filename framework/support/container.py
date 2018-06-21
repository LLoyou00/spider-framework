# encoding=utf-8

import queue
import json
from framework.support.utils import request_to_dict
from framework.support.utils import request_from_dict


class LocalContainer:
    _queue = queue.Queue()

    def put(self, obj):
        self._queue.put(obj)

    def get(self):
        return self._queue.get()

    def empty(self):
        return self._queue.qsize() == 0


class RedisContainer:

    def __init__(self, redis, spider, key='CONTAINER'):
        self._redis = redis
        self._key = key
        self._spider = spider

    def put(self, obj):
        self._redis.lpush(self._key, json.dumps(request_to_dict(obj, self._spider)))

    def get(self):
        return request_from_dict(json.loads(self._redis.rpop(self._key)), self._spider)

    def empty(self):
        return self._redis.llen(self._key) == 0
