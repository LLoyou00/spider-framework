import lxml.html


class Response(object):
    def __init__(self, url, content):
        self.content = content
        self.url = url
        self._etree = lxml.html.fromstring(self.content)

    def xpath(self, param=None):
        return self._etree.xpath(param)

    def cssselect(self, param=None):
        return self._etree.cssselect(param)
