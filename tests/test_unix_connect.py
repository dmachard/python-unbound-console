from unbound_console import RemoteControl
import unittest

class TestUnixConnect(unittest.TestCase):
    def test_status(self):
        """connect and get status"""             
        rc = RemoteControl(unix_sock="/var/run/unbound-console.sock")
        o = rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")