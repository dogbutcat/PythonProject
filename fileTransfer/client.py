import socket
import os


class Client:
    def __init__(self, *args):
        # container = {'key': '', 'data': ''}
        self.ip_port = tuple(args) if len(args) is not 0 else ('127.0.0.1', 8080)
        self.sk = socket.socket()
        self.sk.connect(self.ip_port)
        self._path = ''
        self._cmd = ''

    def run(self):
        while True:
            file_name = os.path.basename(self.path)
            file_size = os.stat(self.path).st_size
            self.sk.send((self.cmd + '|' + file_name + '|' + str(file_size)).encode())
            send_size = 0
            with open(self.path, 'rb') as f:
                flag = True
                while flag:
                    if send_size + 1024 > file_size:
                        data = f.read(file_size - send_size)
                        flag = False
                    else:
                        data = f.read(1024)
                        send_size += 1024
                    self.sk.send(data)
            break

    def get_input(self):
        input_data = input('path:')
        self._cmd, self._path = input_data.split('|')

    @property
    def cmd(self):
        return self._cmd

    @cmd.setter
    def cmd(self, cmd):
        self._cmd = cmd

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def __del__(self):
        self.sk.close()
        del self.sk
