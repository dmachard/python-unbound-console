from unbound_console import RemoteControl
import unittest

class TestConnect(unittest.TestCase):
    def test_status(self):
        """connect and get status"""             
        rc = RemoteControl(host="127.0.0.1", port=8953)
        o = rc.send_command(cmd="status")
        self.assertRegex(o, ".*is running.*")