from framework.support.container import LocalContainer
from framework.support.container import RedisContainer
from framework.support.filter import BloomFilter
from framework.support.filter import MemoryBitMap
from framework.support.filter import RedisBitMap


class Scheduler(object):
    _container = None
    _filter = None

    def add_request(self, request):
        if self._filter.marked(request.hash()):
            return

        self._container.put(request)
        self._filter.mark(request.hash())

    def get_request(self):
        return self._container.get()

    def has_more(self):
        return not self._container.empty()


class LocalScheduler(Scheduler):
    def __init__(self):
        self._container = LocalContainer()
        self._filter = BloomFilter(MemoryBitMap())


class RedisScheduler(Scheduler):
    def __init__(self, redis, spider):
        self._container = RedisContainer(redis, spider, key='SCHEDULER')
        self._filter = BloomFilter(RedisBitMap(redis))
