from framework.spider import Spider as _Spider
from framework.engine import Engine
from framework.http.request import Request
from pipeline import PrintPipeline
from item import ArticleItem
import redis


class Spider(_Spider):
    start_url = "http://blog.jobbole.com/all-posts/"

    def parse(self, response):
        for post in response.cssselect('.archive-title'):
            url = post.get('href')
            yield Request(url, self.article_parser)

        next_page = response.cssselect('.navigation .next')[0].get('href')
        if next_page:
            yield Request(next_page, self.parse)

    def article_parser(self, response):
        item = ArticleItem()
        item.title = response.xpath('//div[@class="entry-header"]/h1/text()')[0]
        item.url = response.url
        yield item


if __name__ == '__main__':
    engine = Engine(Spider(), redis.Redis('192.168.222.134'))
    engine.set_pipeline(ArticleItem, PrintPipeline())
    engine.driver()

