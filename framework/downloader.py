import aiohttp
import asyncio
from threading import Thread
import traceback


class Downloader:
    _event_loop = None

    def start(self):
        self._event_loop = asyncio.new_event_loop()
        Thread(target=lambda loop: asyncio.set_event_loop(loop) or loop.run_forever(),
               args=(self._event_loop,)).start()

    def stop(self):
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)

    async def get_content(self, request, callback):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request.url) as res:
                    callback(request, await res.text())
        except Exception:
            traceback.print_exc()

    def down(self, request, callback):
        asyncio.run_coroutine_threadsafe(self.get_content(request, callback), self._event_loop)


if __name__ == '__main__':
    from framework.http.request import Request

    download = Downloader()
    download.start()
    download.down(Request("http://www.baidu.com", lambda: None),
                  lambda req, res: print(req, res) or download.stop())
