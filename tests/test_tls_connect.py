from unbound_console import RemoteControl, RemoteControlAsync
import unittest

class TestTlsConnect(unittest.TestCase):
    def test_status(self):
        """connect and get status"""             
        rc = RemoteControl(host="127.0.0.1", port=8953,
                           server_cert = "/tmp/unbound_server.pem", 
                           client_cert= "/tmp/unbound_control.pem",
                           client_key= "/tmp/unbound_control.key")
        o = rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")


class TestAsyncTlsConnect(unittest.IsolatedAsyncioTestCase):
    async def test_status(self):
        """connect and get status"""
        rc = RemoteControlAsync(host="127.0.0.1", port=8953,
                           server_cert = "/tmp/unbound_server.pem",
                           client_cert= "/tmp/unbound_control.pem",
                           client_key= "/tmp/unbound_control.key")
        o = await rc.send_command(cmd="status")
        print(o)
        self.assertRegex(o, ".*is running.*")
