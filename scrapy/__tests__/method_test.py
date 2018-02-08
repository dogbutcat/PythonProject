from unittest import TestCase
from unittest.mock import patch
from translate_Uri import calculateSign, main_req, opener


class TranslateSignTestCase(TestCase):

    def setUp(self):
        self.gtk = '320305.131321201'

    def test_calculate_sign(self):
        ret_val = calculateSign('translate me', self.gtk)
        ret_val_2 = calculateSign(
            'translate metranslate metranslate metranslate metranslate metranslate metranslate metranslate metranslate metranslate me',
            self.gtk)
        ret_val_3 = calculateSign(
            '𠮷',
            self.gtk)
        assert ret_val == '200239.519454'
        assert ret_val_2 == '516462.197215'
        # assert ret_val_3 == '491337.236664'

    @patch.object(opener, 'open')
    @patch('urllib.request.Request')
    def test_request(self, mock_request, mock_opener):
        mock_request.return_value = 'return_value'
        mock_opener.return_value = True
        ret_val = main_req('a')
        assert ret_val is True
