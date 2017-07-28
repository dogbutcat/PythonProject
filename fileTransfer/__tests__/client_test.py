from unittest import TestCase
from unittest.mock import patch, mock_open, Mock
from client import Client


class ClientTestCase(TestCase):
    @patch('client.socket.socket')
    def setUp(self, mock_socket):
        self.ip_port = ('127.0.0.1', 8080)
        self.c = Client()

    def test_socket_connect(self):
        self.c.sk.connect.assert_called_with(self.ip_port)

    @patch('builtins.input', side_effect=['input'])
    def test_get_input_error(self, mock_input):
        self.assertRaises(ValueError, self.c.get_input)

    @patch('builtins.input', side_effect=['input|file.py'])
    def test_get_input_validate(self, mock_input):
        self.c.get_input()
        assert self.c.cmd == 'input'
        assert self.c.path == 'file.py'

    def test_set_cmd(self):
        self.c.cmd = 'send'
        assert self.c.cmd == 'send'

    def test_set_path(self):
        self.c.path = 'file2.py'
        assert self.c.path == 'file2.py'

    @patch('client.os.path.basename')
    @patch('client.os.stat')
    @patch('builtins.open', mock_open(read_data='data'))  # mock in patch not occupy args
    def test_run_file_size_lt_1024(self, mocked_stat, mock_basename):
        mocked_stat.return_value.st_size = 10
        self.c.run()

    @patch('client.os.path.basename')
    @patch('client.os.stat')
    @patch('builtins.open', mock_open(read_data='data' * 1024))
    def test_run_file_size_gt_1024(self, mocked_stat, mock_basename):
        mocked_stat.return_value.st_size = 1024 * 4
        self.c.run()
