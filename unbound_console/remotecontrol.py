import asyncio
import socket
import ssl
from abc import ABCMeta, abstractmethod

import yaml

UC_PORT = 8953
UC_VERSION = b"1"


class RemoteControlBase(metaclass=ABCMeta):
    def __init__(self, host="127.0.0.1", port=UC_PORT, server_cert = None,
                       client_cert=None, client_key=None, unix_sock=None):
        """remote control class"""
        self.rc_host = host
        self.rc_port = port
        self.rc_unix = unix_sock

        self.s_cert = server_cert
        self.c_key = client_key
        self.c_cert = client_cert

    def setup_ssl_ctx(self):
        """setup the ssl context and return it"""
        ssl_ctx = None

        # if provided, validate certificate
        if self.s_cert and self.c_key and self.c_cert:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                 cafile=self.s_cert)
            ssl_ctx.load_cert_chain(certfile=self.c_cert, keyfile=self.c_key)
            ssl_ctx.check_hostname = False

        return ssl_ctx

    @abstractmethod
    def send_command(self, cmd, data_list=""):
        """send command return output"""
        pass

    @abstractmethod
    def load_zone(self, data_yaml):
        """add local zone"""
        pass


class RemoteControl(RemoteControlBase):
    def _get_remote_control_socket(self):
        """connect and return a remote control socket"""
        sock = None
        # prepare unix socket
        if self.rc_unix != None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.rc_unix)
            return sock

        # prepare tcp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(1.0)

        # setup ssl context ?
        ssl_ctx = self.setup_ssl_ctx()
        if ssl_ctx is not None:
            sock = ssl_ctx.wrap_socket(sock, server_side=False)

        # connect to the server
        sock.connect((self.rc_host, self.rc_port))

        return sock

    def send_command(self, cmd, data_list=""):
        sock = self._get_remote_control_socket()

        # send the command
        sock.send(f"UBCT{UC_VERSION} {cmd}\n".encode())

        if cmd.encode() in [ b"local_zones", b"local_zones_remove",
                             b"local_datas", b"view_local_datas",
                             b"local_datas_remove", b"view_local_datas_remove",
                             b"load_cache" ]:
            for line in data_list:
                sock.send(f"{line}\n".encode())

            if cmd.encode() != b"load_cache":
                sock.send(b"\x04\x0a")

        # wait to receive all data
        buf = b''
        recv = True
        while recv:
            data = sock.recv(1024)
            buf += data
            if not data:
                recv = False
                break

        # close the connection
        sock.close()

        # return the data
        o = []
        for l in buf.splitlines():
            o.append(l.decode("utf-8"))
        return "\n".join(o)

    def load_zone(self, data_yaml):
        y = yaml.safe_load(data_yaml)

        zone = y.get("zone", {})
        zone_name = zone.get("name", None)
        zone_type = zone.get("type", "static")
        zone_records = zone.get("records", [])

        if zone_name is None:
            raise Exception("name zone not provided")

        o = self.send_command(cmd=f"local_zone {zone_name} {zone_type}")

        for record in zone_records:
            o = self.send_command(cmd=f"local_data {record}")

        return o


class RemoteControlAsync(RemoteControlBase):
    async def _get_remote_control_streams(self):
        """
        connect to remote control and return the stream reader/writer
        """
        if self.rc_unix != None:
            return await asyncio.open_unix_connection(
                self.rc_unix,
                ssl=self.setup_ssl_ctx(),
            )

        return await asyncio.open_connection(
            self.rc_host,
            self.rc_port,
            ssl=self.setup_ssl_ctx(),
        )

    async def send_command(self, cmd, data_list=""):
        reader, writer = await self._get_remote_control_streams()

        writer.write(f"UBCT{UC_VERSION} {cmd}\n".encode())
        await writer.drain()

        if cmd.encode() in [ b"local_zones", b"local_zones_remove",
                             b"local_datas", b"view_local_datas",
                             b"local_datas_remove", b"view_local_datas_remove",
                             b"load_cache" ]:
            for line in data_list:
                writer.write(f"{line}\n".encode())
                await writer.drain()

            if cmd.encode() != b"load_cache":
                writer.write(b"\x04\x0a")
                await writer.drain()

        lines = []

        # read all lines until EOF
        async for line in reader:
            lines.append(line.decode("utf-8").rstrip("\n"))

        # close the writer
        writer.close()
        await writer.wait_closed()

        return "\n".join(lines)

    async def load_zone(self, data_yaml):
        y = yaml.safe_load(data_yaml)

        zone = y.get("zone", {})
        zone_name = zone.get("name", None)
        zone_type = zone.get("type", "static")
        zone_records = zone.get("records", [])

        if zone_name is None:
            raise Exception("name zone not provided")

        o = await self.send_command(cmd=f"local_zone {zone_name} {zone_type}")

        for record in zone_records:
            o = await self.send_command(cmd=f"local_data {record}")

        return o
