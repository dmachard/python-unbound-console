import asyncio
import socket
import ssl
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List

import yaml

UC_PORT = 8953
UC_VERSION = b"1"

CMDS_WITH_DATA = (
    "local_zones", "local_zones_remove",
    "local_datas", "view_local_datas",
    "local_datas_remove", "view_local_datas_remove",
    "load_cache",
)


@dataclass
class LocalZone:
    name: str
    type: str = "static"
    records: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            raise ZoneBlankException("name zone not provided")


class ZoneBlankException(Exception):
    pass


class RemoteControlBase(metaclass=ABCMeta):
    def __init__(self, host="127.0.0.1", port=UC_PORT, server_cert = None,
                       client_cert=None, client_key=None, unix_sock=None):
        """remote control class"""
        self.rc_host = host
        self.rc_port = port
        self.rc_unix = unix_sock

        self.ssl_ctx = None

        # if provided, validate certificate
        if server_cert and client_cert and client_key:
            self.ssl_ctx = self.get_ssl_ctx(server_cert, client_cert, client_key)

    @staticmethod
    def get_ssl_ctx(server_cert, client_cert, client_key):
        """setup the ssl context and return it"""
        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                cafile=server_cert)
        ssl_ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
        ssl_ctx.check_hostname = False
        return ssl_ctx

    @staticmethod
    def yaml_to_local_zone(yaml_data: str) -> "LocalZone":
        yaml_data = yaml.safe_load(yaml_data)
        zone=yaml_data.get("zone", {})
        return LocalZone(
            name=zone.get("name", None),
            type=zone.get("type", "static"),
            records=zone.get("records", []),
        )

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
        if self.rc_unix is not None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.rc_unix)
            return sock

        # prepare tcp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(1.0)

        if self.ssl_ctx is not None:
            sock = self.ssl_ctx.wrap_socket(sock, server_side=False)

        # connect to the server
        sock.connect((self.rc_host, self.rc_port))

        return sock

    def send_command(self, cmd, data_list=""):
        sock = self._get_remote_control_socket()

        # send the command
        sock.send(f"UBCT{UC_VERSION.decode()} {cmd}\n".encode())

        if cmd in CMDS_WITH_DATA:
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
        zone = self.yaml_to_local_zone(data_yaml)

        o = self.send_command(cmd=f"local_zone {zone.name} {zone.type}")

        for record in zone.records:
            o = self.send_command(cmd=f"local_data {record}")

        return o


class RemoteControlAsync(RemoteControlBase):
    async def _get_remote_control_streams(self):
        """
        connect to remote control and return the stream reader/writer
        """
        if self.rc_unix is not None:
            return await asyncio.open_unix_connection(
                self.rc_unix,
                ssl=self.ssl_ctx,
            )

        return await asyncio.open_connection(
            self.rc_host,
            self.rc_port,
            ssl=self.ssl_ctx,
        )

    async def send_command(self, cmd, data_list=""):
        reader, writer = await self._get_remote_control_streams()

        writer.write(f"UBCT{UC_VERSION.decode()} {cmd}\n".encode())
        await writer.drain()

        if cmd in CMDS_WITH_DATA:
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
        zone = self.yaml_to_local_zone(data_yaml)

        o = await self.send_command(cmd=f"local_zone {zone.name} {zone.type}")

        for record in zone.records:
            o = await self.send_command(cmd=f"local_data {record}")

        return o
