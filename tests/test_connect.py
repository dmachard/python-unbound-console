from unbound_console import RemoteControl, RemoteControlAsync
import unittest

class TestTcpConnect(unittest.TestCase):
    def test_status(self):
        """connect and get status"""             
        rc = RemoteControl(host="127.0.0.1", port=8953)
        o = rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")


class TestAsyncTcpConnect(unittest.IsolatedAsyncioTestCase):
    async def test_status(self):
        """connect and get status"""
        rc = RemoteControlAsync(host="127.0.0.1", port=8953)
        o = await rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")
