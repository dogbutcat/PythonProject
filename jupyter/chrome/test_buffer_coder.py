import unittest
from buffer_coder import BufferCoder

class TestBufferCoder(unittest.TestCase):
    def test_encode_decode(self):
        buffer_coder = BufferCoder()
        data = 'type@=loginreq/roomid@=610588/dfl@=sn@AA=105@ASss@AA=1/username@=visitor1888972/uid@=1193071308/ver@=20190610/aver@=218101901/ct@=0/'
        # data = 'type@=loginreq/'
        encoded_data = buffer_coder.encode(data)
        # print((encoded_data))

        # Test decoding a complete message
        def on_message(decoded_data):
            self.assertEqual(decoded_data, data)

        buffer_coder.decode(encoded_data, on_message)
        self.assertEqual(buffer_coder.buffer, b'')

        # Test decoding two complete messages in a row
        buffer_coder.decode(encoded_data + encoded_data, on_message)
        self.assertEqual(buffer_coder.buffer, b'')

if __name__ == '__main__':
    unittest.main()
