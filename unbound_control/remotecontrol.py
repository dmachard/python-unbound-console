
import socket
import ssl

UC_PORT = 8953
UC_VERSION = b"1"

class RemoteControl:
    def __init__(self, host="127.0.0.1", port=UC_PORT, server_cert = None, 
                       client_cert=None, client_key=None):
        """remote control class"""
        self.rc_host = host
        self.rc_port = port
        
        self.sock = None
        self.sock_timeout = 1.0
        
        self.s_cert = server_cert
        self.c_key = client_key
        self.c_cert = client_cert
        
    def setup_ssl_ctx(self):
        """setup ssl context"""
        ssl_ctx = None
        
        # if provided, validate certificate
        if self.s_cert and self.c_key and self.c_cert:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                 cafile=self.s_cert)
            ssl_ctx.load_cert_chain(certfile=self.c_cert, keyfile=self.c_key)
            ssl_ctx.check_hostname = False

        return ssl_ctx
        
    def connect_to(self):
        """connect to remote control"""
        # prepare a tcp socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(self.sock_timeout)
        
        # setup ssl context ?
        ssl_ctx = self.setup_ssl_ctx()
        if ssl_ctx is not None:
            self.sock = ssl_ctx.wrap_socket(self.sock, server_side=False)

        # connect to the server
        self.sock.connect((self.rc_host, self.rc_port))
        
    def send_command(self, cmd):
        """send command return output"""
        # connect to the remote server
        self.connect_to()

        # send the command
        self.sock.send(b"UBCT%s %s\n" % (UC_VERSION, cmd.encode()))
        
        # wait to receive all data
        buf = b''
        recv = True
        while recv:
            data = self.sock.recv(5)
            buf += data
            if not data:
                recv = False
                break
        
        # close the connection
        self.sock.close()
        
        # return the data
        o = []
        for l in buf.splitlines():
            o.append(l.decode("utf-8"))
        return "\n".join(o)
