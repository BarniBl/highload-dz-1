import socket
from src.response import HttpResponse

max_request_len = 64 * 1024


def handler_client(listen_socket, document_root, lock):
    while True:
        client_socket, client_address = listen_socket.accept()

        try:
            request = read_from_socket(client_socket)
            response = HttpResponse(request, document_root).create_response()
            lock.acquire()
            try:
                client_socket.sendall(response)
            finally:
                lock.release()
            client_socket.close()
        except (ConnectionError, BrokenPipeError):
            print('Socket error')
        finally:
            print('Closed connection to {}'.format(client_address))
            client_socket.close()


def create_socket(host, port):
    new_socket = socket.socket()
    new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_socket.bind((host, port))
    new_socket.listen(10)
    return new_socket


def read_from_socket(client_sock) -> str:
    buffer = ''

    while True:
        data = client_sock.recv(1024)

        if not data:
            return ''

        buffer += data.decode()
        if buffer.find('\r\n\r\n'):
            break
        if len(buffer) >= max_request_len:
            return ''

    return buffer
