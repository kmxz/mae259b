import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST_NAME = 'localhost'
PORT_NUMBER = 8080


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.strip().lstrip('/')
        if path == '':
            self.serve_static('visualize/index.html', 'text/html')
        elif path.startswith('data') and path.endswith('.json'):
            self.serve_static(path, 'application/json')
        elif path == 'list':
            self.serve_list('data')
        else:
            self.send_response(404)
            self.end_headers()

    def serve_list(self, path):
        rec = [(parent[len(path):], [f for f in files if f.endswith('.json')]) for (parent, dirs, files) in os.walk(path)]
        out = {k: v for (k, v) in rec if len(v)}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(out).encode('utf8'))

    def serve_static(self, path, mime_type):
        try:
            file = open(path, 'rb')
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.end_headers()
        self.wfile.write(file.read())


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), Handler)
    print('Please open http://%s:%s/ in your web browser' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
