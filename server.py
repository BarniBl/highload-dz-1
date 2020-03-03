import threading
from src import net_lib
from multiprocessing import Lock

CONFIG_PATH = './src/httpd.conf'
HOST = '0.0.0.0'
PORT = 8000


def read_cfg_file():
    cfg_file = {}
    try:
        cfg_file = open(CONFIG_PATH, 'r')
    except FileNotFoundError:
        exit('Config file {} not found'.format(CONFIG_PATH))

    cfg_file_data = cfg_file.read().split('\n')
    cfg_file.close()

    cfg_data_map = {}
    for string in cfg_file_data:
        string_values = string.split()
        cfg_data_map[string_values[0]] = string_values[1]

    return cfg_data_map


if __name__ == '__main__':
    cfg_data = read_cfg_file()

    listen_socket = net_lib.create_socket(HOST, PORT)
    print('Listening on {}'.format(listen_socket.getsockname()))

    thread_pool = []
    lock = Lock()
    for i in range(int(cfg_data['threads_limit'])):
        new_thread = threading.Thread(target=net_lib.handler_client,
                                      args=[listen_socket, cfg_data['static_root'], lock],
                                      daemon=True)
        thread_pool.append(new_thread)
        new_thread.start()

    for thread in thread_pool:
        thread.join()
