from unbound_console import RemoteControl
import unittest

class TestZone(unittest.TestCase):
    def test1_add_zone(self):
        """add zone"""             
        rc = RemoteControl(host="127.0.0.1", port=8953,
                           server_cert = "/etc/unbound/unbound_server.pem", 
                           client_cert= "/etc/unbound/unbound_control.pem",
                           client_key= "/etc/unbound/unbound_control.key")
                           
        zone_yaml = """
zone:
  name: test.
  type: static
  resource-records:
    - "router.test. 86400 IN A 192.168.0.1"
  pointer-records:
    - "192.168.0.1  86400 router.test."
"""

        o = rc.load_zone(data_yaml=zone_yaml)
        self.assertRegex(o, "ok")