#!/usr/bin/env python2
# TODO: https://www.piware.de/2011/01/creating-an-https-server-in-python/

import BaseHTTPServer
import re
import urlparse
import cgi
import time
import json

import signin


paths = [
        (r'^/$', signin.Handler()),
        ]


class AttendanceHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def get_handler(self):
        path = self.path
        if '?' in path:
            path = path[:path.find('?')]
        for pattern, handler in paths:
            if re.match(pattern, path):
                return handler
        return None

    def do_HEAD(self):
        self.handler = self.get_handler()
        if self.handler:
            if not self.handler.custom_headers:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        if self.handler:
            get_vars = urlparse.parse_qs(self.path)
            post_vars = {}
            self.handler.handle(self, get_vars, post_vars)

    def do_POST(self):
        self.do_HEAD()
        if self.handler:
            get_vars = urlparse.parse_qs(self.path)

            c_type, p_dict = cgi.parse_header(self.headers['content-type'])
            if c_type == 'multipart/form-data':
                post_vars = cgi.parse_multipart(self.rfile, p_dict)
            elif c_type == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                post_vars = urlparse.parse_qs(
                        self.rfile.read(length),
                        keep_blank_values=1)
            else:
                post_vars = {}

            self.handler.handle(self, get_vars, post_vars)


def serve(host, port):
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((host, port), AttendanceHandler)
    #httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/path/to/cert.pem', server_side=True)
    print time.asctime(), "Server Starts - %s:%s" % (host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (host, port)

if __name__ == '__main__':
    serve('', 9000)
