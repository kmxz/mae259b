import asyncio
import os
import json

import shutil
from aiohttp import web
from aiohttp.web import Response


async def index(request):
    html = open('visualize/index.html', 'r')
    content = html.read()
    html.close()
    return Response(text=content, content_type='text/html')

async def list(request):
    rec = [(parent[len('data'):], [f for f in files if f.endswith('.json')]) for (parent, dirs, files) in os.walk('data')]
    out = {k: v for (k, v) in rec if len(v)}
    return Response(text=json.dumps(out), content_type='application/json')

async def file_upload(request):
    data = await request.post()
    id = data['id']
    time = data['time']
    file = data['image'].file
    out = open('screenshots/%s-%s.png' % (id, time), 'wb')
    shutil.copyfileobj(file, out)
    out.close()
    return Response(text='OK', content_type='text/plain')

async def on_prepare(request, response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'

app = web.Application()
app.on_response_prepare.append(on_prepare)
app.router.add_route('GET', '/', index)
app.router.add_static('/data', 'data')
app.router.add_static('/static', 'visualize')
app.router.add_route('GET', '/list', list)
app.router.add_route('POST', '/save', file_upload)

loop = asyncio.get_event_loop()

print("Please open your web browser to interact")
web.run_app(app, host='127.0.0.1', port=8080)