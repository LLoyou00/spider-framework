from framework.scheduler import LocalScheduler
from framework.scheduler import RedisScheduler
from framework.downloader import Downloader
from framework.http.response import Response
from framework.http.request import Request
from framework.item import Item


class Engine:
    _max_connection = 10
    _current_connection = 0
    _pipelines = dict()

    def __init__(self, spider, redis=None):
        if redis is not None:
            self._scheduler = RedisScheduler(redis, spider)
        else:
            self._scheduler = LocalScheduler()
        self._downloader = Downloader()
        self._spider = spider

    def run(self):
        self._downloader.start()
        while self._continuable():
            if (self._current_connection <= self._max_connection) and self._scheduler.has_more():
                self._current_connection += 1
                self._downloader.down(self._scheduler.get_request(), self.down_handle)

        self._downloader.stop()

    def _continuable(self):
        return self._scheduler.has_more() or self._current_connection != 0

    def down_handle(self, req, res):
        for obj in req.callback(Response(req.url, res)):
            if isinstance(obj, Request):
                self._scheduler.add_request(obj)
            elif isinstance(obj, Item):
                self._pipelines[obj.__class__] and self._pipelines[obj.__class__].process_item(obj)
        self._current_connection -= 1

    def set_max_connection(self, value):
        self._max_connection = value

    def set_pipeline(self, item, obj):
        self._pipelines[item] = obj

    def driver(self):
        for request in self._spider.start_request():
            self._scheduler.add_request(request)

        self.run()
