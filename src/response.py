import os
from datetime import datetime
from urllib import parse

content_types = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash',
    'txt': 'text/plain'
}

status_types = {
    '200': 'OK',
    '403': 'Forbidden',
    '404': 'Not Found',
    '405': 'Method Not Allowed'
}

GET = 'GET'
HEAD = 'HEAD'
INFO = 'HTTP/1.1'
index = 'index.html'


class HttpResponse:
    def __init__(self, request, document_root):
        self.headers = {
            'Content-Type:': '',
            'Content-Length:': '',
            'Date:': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Server:': 'server/1.0',
            'Connection:': 'close'
        }
        self.request = request
        self.request_path = ''
        self.file_path = ''
        self.document_root = document_root

    def add_header(self, type, body):
        self.headers.update({type: body})

    def response_with_error(self, code):
        response = INFO + ' {} {}\r\n'.format(code, status_types[str(code)])
        response += '{} {}\r\n'.format('Date:', str(self.headers['Date:']))
        response += '{} {}\r\n'.format('Server:', str(self.headers['Server:']))
        response += '{} {}\r\n'.format('Connection:', str(self.headers['Connection:']))
        response += '\n'
        return response.encode()

    def response_get_head(self, param=''):
        try:
            file = open(self.file_path, 'rb')
            body = file.read()
            file.close()

            self.add_header('Content-Length:', str(len(body)))

            response = 'HTTP/1.1 {} {}\r\n'.format(200, status_types['200'])
            for key in self.headers:
                response += '{} {}\r\n'.format(key, str(self.headers[key]))

            if param == GET:
                response += '\n'
                return response.encode() + body

            response += '\r\n'
            return response.encode()
        except IOError:
            return self.response_with_error(404)

    def create_response(self):
        request_first_line = self.request.split('\r\n')[0].split(' ')

        request_method = request_first_line[0]
        if not (request_method == GET or request_method == HEAD):
            return self.response_with_error(405)

        self.request_path = parse.urlparse(parse.unquote(request_first_line[1])).path

        if self.request_path.find('../') != -1:
            return self.response_with_error(404)

        if os.path.isdir(self.request_path):
            self.file_path = self.document_root + self.request_path + index
            if not (os.path.isfile(self.file_path)):
                return self.response_with_error(403)
        else:
            self.file_path = self.document_root + self.request_path

        if not os.path.isfile(self.file_path):
            return self.response_with_error(404)
        self.add_header('Content-Type:', content_types[self.file_path.split('.')[-1]])

        if request_method == GET:
            return self.response_get_head(GET)

        return self.response_get_head()
