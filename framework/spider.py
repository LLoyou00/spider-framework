from framework.http.request import Request


class Spider:
    start_url = None

    def start_request(self):
        yield Request(self.start_url, self.parse)

    def parse(self, response):
        pass
