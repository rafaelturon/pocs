#!/usr/bin/env python

'''
Simple and functional REST server for Python (2.7) using no dependencies beyond the Python standard library.

Features:

* Map URI patterns using regular expressions
* All responses and payloads are converted to/from JSON for you
* Correct HTTP response codes and basic error messages
* Simple REST client included! use the rest_call_json() method

As an example, let's support a simple key/value store. To test from the command line using curl:

curl "http://localhost:8080/record"
curl -X POST -d '{"jsonrpc": "2.0", "method": "addPrinter", "params": {"printerUrl": "full-path", "installUrl": "full-path"}, "id": "XXX-YYY-ZZZ"}' "http://localhost:8080/record/"

@author: Tal Liron (tliron @ github.com)
'''

import sys, os, re, shutil, json, urllib, urllib2, BaseHTTPServer
from printer_wrapper import PrinterWrapper

# Fix issues with decoding HTTP responses
reload(sys)
sys.setdefaultencoding('utf8')

here = os.path.dirname(os.path.realpath(__file__))

records = {}

def get_about(handler):
    return "RPC-Json 1.0.0.0"

def get_record(handler):
    key = urllib.unquote(handler.path[8:])
    return records[key] if key in records else None

def set_record(handler):
    key = urllib.unquote(handler.path[8:])
    payload = handler.get_payload()
    records[key] = payload
    return records[key]

def delete_record(handler):
    key = urllib.unquote(handler.path[8:])
    del records[key]
    return True # anything except None shows success

def rest_call_json(url, payload=None, with_payload_method='POST'):
    'REST call with JSON decoding of the response and JSON payloads'
    if payload:
        if not isinstance(payload, basestring):
            payload = json.dumps(payload)
        # PUT or POST
        response = urllib2.urlopen(MethodRequest(url, payload, {'Content-Type': 'application/json'}, method=with_payload_method))
    else:
        # GET
        response = urllib2.urlopen(url)
    response = response.read().decode()
    return json.loads(response)

class MethodRequest(urllib2.Request):
    'See: https://gist.github.com/logic/2715756'
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return self._method if self._method is not None else urllib2.Request.get_method(self, *args, **kwargs)

class RESTRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.printer = PrinterWrapper()
        self.routes = {
            r'^/about/': {'GET': get_about, 'media_type': 'application/json'},
            r'^/record/': {'GET': get_record, 'POST': set_record, 'media_type': 'application/json'}}
        
        return BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def do_HEAD(self):
        self.handle_method('HEAD')
    
    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')
    
    def get_payload(self):
        payload_len = int(self.headers.getheader('content-length', 0))
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload)
        return payload
        
    def handle_method(self, method):
        route = self.get_route()
        if route is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('Route not found\n')
        else:
            if method == 'HEAD':
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header('Content-type', route['media_type'])
                self.end_headers()
            else:
                if method in route:
                    content = route[method](self)
                    if content is not None:
                        self.send_response(200)
                        if 'media_type' in route:
                            self.send_header('Content-type', route['media_type'])
                        self.end_headers()
                        if method == 'GET':
                            result = self.get_response(self.printer.list_printers(), 'id-get')
                            self.wfile.write(result)
                        else:
                            result = self.get_response(self.printer.remove_printer(content), 'id-remove')
                            self.wfile.write(result)
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write('Not found\n')
                else:
                    self.send_response(405)
                    self.end_headers()
                    self.wfile.write(method + ' is not supported\n')
                    
    
    def get_response(self, result, id):
        data = {}
        data['jsonrpc'] = '2.0'
        data['result'] = result
        data['id'] = id
        return json.dumps(data)

    def get_route(self):
        for path, route in self.routes.iteritems():
            if re.match(path, self.path):
                return route
        return None

def rest_server(port):
    'Starts the REST server'
    http_server = BaseHTTPServer.HTTPServer(('', port), RESTRequestHandler)
    print 'Starting HTTP server at port %d' % port
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    print 'Stopping HTTP server'
    http_server.server_close()

def main(argv):
    rest_server(8080)

if __name__ == '__main__':
    main(sys.argv[1:])
