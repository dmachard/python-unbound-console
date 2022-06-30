from unbound_console import RemoteControl, RemoteControlAsync

import unittest
import dns.resolver

my_resolver = dns.resolver.Resolver(configure=False)
my_resolver.nameservers = [ '127.0.0.1' ]
my_resolver.port = 5300

class TestZone(unittest.TestCase):
    def test1_load_zone(self):
        """load zone"""             
        rc = RemoteControl(host="127.0.0.1", port=8953,
                           server_cert = "/tmp/unbound_server.pem", 
                           client_cert= "/tmp/unbound_control.pem",
                           client_key= "/tmp/unbound_control.key")
                           
        zone_yaml = """
zone:
  name: test.
  type: static
  records:
    - "router.test. 86400 IN A 192.168.0.1"
    - "192.168.0.1 86400 IN PTR router.test."
"""

        o = rc.load_zone(data_yaml=zone_yaml)
        print(o)

        r = my_resolver.resolve('router.test', 'a')
        print(r.response)
        self.assertRegex(str(r.response), ".*192.168.0.1.*")


class TestZoneAsync(unittest.IsolatedAsyncioTestCase):
    async def test1_load_zone(self):
        """load zone"""
        rc = RemoteControlAsync(host="127.0.0.1", port=8953,
                           server_cert = "/tmp/unbound_server.pem",
                           client_cert= "/tmp/unbound_control.pem",
                           client_key= "/tmp/unbound_control.key")

        zone_yaml = """
zone:
  name: test.
  type: static
  records:
    - "router.test. 86400 IN A 192.168.0.1"
    - "192.168.0.1 86400 IN PTR router.test."
"""

        o = await rc.load_zone(data_yaml=zone_yaml)
        print(o)

        r = my_resolver.resolve('router.test', 'a')
        print(r.response)
        self.assertRegex(str(r.response), ".*192.168.0.1.*")
