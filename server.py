import asyncio
import threading
import os
import json

from aiohttp import web
from aiohttp.web import Response
from aiohttp_sse import sse_response

from run import runDER


queue = asyncio.Queue()


class ComputeThread(threading.Thread):

    def put(self, content):
        loop.call_soon_threadsafe(queue.put_nowait, content)

    def run(self):
        runDER(self)


th = ComputeThread()


async def task(request):
    async with sse_response(request) as response:
        try:
            while not response.task.done():
                payload = await queue.get()
                await response.send(payload)
                queue.task_done()
        finally:
            pass
    return response


async def index(request):
    html = open('visualize/index.html', 'r')
    content = html.read()
    html.close()
    return Response(text=content, content_type='text/html')


async def list(request):
    files = os.scandir('data')
    jsons = [f.name for f in files if f.name.endswith('.json')]
    return Response(text=json.dumps(jsons), content_type='application/json')


app = web.Application()


app.router.add_route('GET', '/', index)
app.router.add_static('/static', 'visualize')
app.router.add_static('/data', 'data')

app.router.add_route('GET', '/task', task)
app.router.add_route('GET', '/list', list)

loop = asyncio.get_event_loop()

print("Please open your web browser to interact")
web.run_app(app, host='127.0.0.1', port=8080)