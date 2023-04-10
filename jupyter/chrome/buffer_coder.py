import struct

class BufferCoder:
    def __init__(self):
        self.buffer = bytes()
        self.little_endian = True
        self.read_length = 0

    def concat(self, *args):
        return b''.join(args)
    
    def decode(self, data, callback, little_endian=None):
        if little_endian is None:
            little_endian = self.little_endian
        self.buffer = self.concat(self.buffer, data)
        while self.buffer and len(self.buffer)>0:
            if self.read_length == 0:
                if len(self.buffer) < 4:
                    return
                self.read_length = struct.unpack_from('<H', self.buffer)[0]
                self.buffer = self.buffer[4:]
            if len(self.buffer) < self.read_length:
                return
            n = self.buffer[8:self.read_length-1].decode('utf-8')
            self.buffer = self.buffer[self.read_length:]
            self.read_length = 0
            callback(n)

    def encode(self, data, little_endian=None):
        if little_endian is None:
            little_endian = self.little_endian
        encoded_data = self.concat(data.encode('utf-8'), b'\x00')
        data_len = len(encoded_data)
        buffer_size = data_len+8
        packed_data = struct.pack('<IIHbb%ds' % data_len, buffer_size, buffer_size, 689,0,0, encoded_data)
        return packed_data
    
