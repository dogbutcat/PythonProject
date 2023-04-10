import unittest
from format_msg import decode_msg

class TestDecodeMsg(unittest.TestCase):
    def test_decode_msg(self):
        self.assertEqual(decode_msg('type@=loginres/roomgroup@=1/groupid@=1666520/rid@=2233/'), 
                         {'type': 'loginres', 'roomgroup': '1', 'groupid': '1666520', 'rid': '2233'})
        
        self.assertEqual(decode_msg('type@=chatmsg/rid@=2233/ct@=2/uid@=123/dnn@=name/sahf@=0/text@=hello/'),
                         {'type': 'chatmsg', 'rid': '2233', 'ct': '2', 'uid': '123', 'dnn': 'name', 'sahf': '0', 'text': 'hello'})
        
        self.assertEqual(decode_msg(''), '')
        
        self.assertEqual(decode_msg('type@=dgb/rid@=123/gfid@=34/sil@=1/'),
                         {'type': 'dgb', 'rid': '123', 'gfid': '34', 'sil': '1'})
        
        self.assertEqual(decode_msg('@='), '@=')
        
if __name__ == '__main__':
    unittest.main()
