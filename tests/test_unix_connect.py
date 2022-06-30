from unbound_console import RemoteControl, RemoteControlAsync
import unittest

class TestUnixConnect(unittest.TestCase):
    def test_status(self):
        """connect and get status"""             
        rc = RemoteControl(unix_sock="/tmp/unbound/unbound-console.sock")
        o = rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")


class TestAsyncUnixConnect(unittest.IsolatedAsyncioTestCase):
    async def test_status(self):
        """connect and get status"""
        rc = RemoteControlAsync(unix_sock="/tmp/unbound/unbound-console.sock")
        o = await rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")
