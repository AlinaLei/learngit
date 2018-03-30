#!/usr/bin/env python
# --coding:utf-8--

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from urllib.parse import urlparse
import sys
sys.path.append('../.settings')
from config import *

playdirandport = {'dir': '', 'port': 0, 'ip': ''}

# MIME-TYPE
mimedic = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.txt': 'text/plain',
    '.avi': 'video/x-msvideo'
}


class HTTPServerRequestHandler(BaseHTTPRequestHandler):

    # def __init__(self,file_path):
    #   super(testHTTPServer_RequestHandler, self).__init__()
    #   self.file_path = curdir + file_path

    def do_GET(self):
        querypath = urlparse(self.path)
        query_path, query = querypath.path, querypath.query

        if query_path.endswith('/'):
            query_path += 'index.html'
        filename, fileext = path.splitext(query_path)
        send_reply = True
        if fileext in mimedic:
            mimetype = mimedic[fileext]
        else:
            mimetype = 'application/octet-stream'

        if send_reply:
            try:
                with open(path.realpath(playdirandport['dir'] + query_path), 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)


def run(name='FILE', file_path='/'):
    playdirandport['dir'] = path.dirname(path.realpath(__file__)) + file_path
    playdirandport['port'] = int(WBASE[name+'_PORT'])
    playdirandport['ip'] = WBASE['WEBserver']
    print('starting server %s, port:%s' % (playdirandport['ip'], playdirandport['port']))

    # Server settings
    server_address = (playdirandport['ip'], playdirandport['port'])
    httpd = HTTPServer(server_address, HTTPServerRequestHandler)
    print('running server...')
    httpd.serve_forever()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            print(sys.argv[1])
            eval(sys.argv[1])
        except Exception as err:
            print('run Exception:', err)
    elif len(sys.argv) == 3:
        run(sys.argv[1], sys.argv[2])
    else:
        run()
