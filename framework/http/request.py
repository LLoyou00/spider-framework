class Request(object):
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback

    def hash(self):
        return self.url + str(hash(self.callback))
