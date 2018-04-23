import asyncio
import threading
import os
import json
from time import time

from aiohttp import web
from aiohttp.web import Response
from aiohttp_sse import sse_response

from run import runDER


class ComputeThread(threading.Thread):

    def __init__(self, task_id):
        super().__init__()
        self.taskId = task_id
        self.previous = []
        self.channels = set()

    def put(self, content):
        obj = content.copy()
        obj['event'] = 'step'
        obj['index'] = len(self.previous)
        self.previous.append(obj)

    def end(self, filename):
        obj = {'event': 'end', 'filename': filename}
        self.previous.append(obj)

    def run(self):
        runDER(self)


computedThreads = dict()
baseTaskId = int(time())


async def start_task(request):
    global baseTaskId
    baseTaskId += 1
    task_id = baseTaskId
    th = ComputeThread(task_id)
    computedThreads[task_id] = th
    th.run()
    return Response(text=json.dumps({'task_id': task_id}), content_type='application/json')


async def task(request):
    task_id = request.match_info['task_id']
    async with sse_response(request) as response:
        try:
            while th.is_alive():
                (tid, payload) = await queue.get()
                print("RECT", tid, payload)
                if tid == task_id:
                    await response.send(payload)
                queue.task_done()
        finally:
            pass
    return response


async def subscribe(request):
    async with sse_response(request) as response:
        queue = asyncio.Queue()
        channels.add(queue)
        try:
            while not response.task.done():
                payload = await queue.get()
                await response.send(payload)
                queue.task_done()
        finally:
            channels.remove(queue)
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

app.router.add_route('POST', '/task', start_task)
app.router.add_route('GET', '/task/{task_id}', task)
app.router.add_route('GET', '/list', list)

loop = asyncio.get_event_loop()

print("Please open your web browser to interact")
web.run_app(app, host='127.0.0.1', port=8080)