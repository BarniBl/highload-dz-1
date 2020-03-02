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

status_codes = {
    '200': 'OK',
    '403': 'Forbidden',
    '404': 'Not Found',
    '405': 'Method Not Allowed'
}

GET = 'GET'
HEAD = 'HEAD'
INFO = 'HTTP/1.1'
INDEX = 'index.html'


class HttpResponse:
    def __init__(self, request, document_root):
        self.request = request
        self.request_path = ''
        self.document_root = document_root

    def response_with_error(self, code):
        response = INFO + ' {} {}\r\n'.format(code, status_codes[str(code)])
        response += '{} {}\r\n'.format('Date:', str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        response += '{} {}\r\n'.format('Server:', 'server/1.0')
        response += '{} {}\r\n'.format('Connection:', 'closed')
        response += '\n'
        return response.encode()

    def response_message(self, method='', file_path=''):
        try:
            file = open(file_path, 'rb')
            body = file.read()
            file.close()

            response = 'HTTP/1.1 {} {}\r\n'.format(200, status_codes['200'])
            response += '{} {}\r\n'.format('Content-Type:', content_types[file_path.split('.')[-1]])
            response += '{} {}\r\n'.format('Content-Length:', os.path.getsize(file_path))
            response += '{} {}\r\n'.format('Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            response += '{} {}\r\n'.format('Server:', 'server/1.0')
            response += '{} {}\r\n'.format('Connection:', 'closed')

            if method == GET:
                response += '\n'
                return response.encode() + body

            response += '\r\n'
            return response.encode()
        except IOError:
            return self.response_with_error(404)

    def get_request_path(self):
        request_first_line = self.request.split('\r\n')[0].split(' ')

        if request_first_line[0] not in [GET, HEAD]:
            return self.response_with_error(405)

        self.request_path = parse.unquote(request_first_line[1])

        return request_first_line[0]

    def create_response(self):
        method = self.get_request_path()

        if self.request_path.find('../') != -1:
            return self.response_with_error(404)

        if self.request_path[-1] == '/':
            file_path = self.document_root + self.request_path + INDEX
            if not (os.path.isfile(file_path)):
                return self.response_with_error(403)
        else:
            file_path = self.document_root + self.request_path

        if method == GET:
            return self.response_message(GET, file_path)

        return self.response_message(HEAD, file_path)
