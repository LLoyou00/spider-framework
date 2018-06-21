from framework.pipeline import Pipeline


class PrintPipeline(Pipeline):
    def process_item(self, item):
        print(item.title + ' ' + item.url)
