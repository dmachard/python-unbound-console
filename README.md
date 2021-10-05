# Python console for unbound server

![Build](https://github.com/dmachard/unbound-remotecontrol/workflows/Build/badge.svg) ![Testing](https://github.com/dmachard/unbound-remotecontrol/workflows/Testing/badge.svg) ![Pypi](https://github.com/dmachard/unbound-remotecontrol/workflows/PyPI/badge.svg)


![unbound 1.12.x](https://img.shields.io/badge/unbound%201.12.x-tested-green) ![unbound 1.13.x](https://img.shields.io/badge/unbound%201.13.x-tested-green) 
![python 3.8.x](https://img.shields.io/badge/python%203.8.x-tested-green) ![python 3.9.x](https://img.shields.io/badge/python%203.9.x-tested-green) 


## Table of contents
* [Installation](#installation)
* [Remote Control on Unbound](#remote-control-on-unbound)
* [Execute command](#execute-command)
* [Loading zone from YAML file](#loading-zone-from-yaml-file)
* [Execute bulk command](#execute-bulk-command)

## Installation

This module can be installed from [pypi](https://pypi.org/project/unbound_console/) website

```python
pip install unbound_console
```

## Remote Control on Unbound

Before to use this utility. You must activate the remote control on your unbound server.
See [config file](https://github.com/dmachard/unbound-remotecontrol/blob/master/tests/unbound_remotecontrol_tls.conf) example. 

### Execute command

You can execute commands with the function `send_command`. See [nlnetlabs documentations](https://www.nlnetlabs.nl/documentation/unbound/unbound-control/) for the full list of available commands.

- Import the module in your code

```python
from unbound_console import RemoteControl
```

- Configure the remote control client with tls support. You can also provide a unix socket `unix_sock="/var/run/unbound-console.sock`.

```python
rc = RemoteControl(host="127.0.0.1", port=8953,
                   server_cert = "/etc/unbound/unbound_server.pem", 
                   client_cert= "/etc/unbound/unbound_control.pem",
                   client_key= "/etc/unbound/unbound_control.key")
```

- Execute a command and get output

```python
o = rc.send_command(cmd="status")
print(o)
```

### Loading zone from YAML file

YAML zone definition example:

```
zone:
  name: home.
  type: static
  records:
    - "router.home. 86400 IN A 192.168.0.1"
    - "192.168.0.1 86400 IN PTR router.test."
```

Call `load_zone` with the yaml file to load-it in your unbound server.

```python
o = rc.load_zone(data_yaml='<yaml content>')
print(o)
```

### Execute bulk command

```python
domains_bulk = []
domains_bulk.append( "www.google.com always_nxdomain")

o = rc.send_command(cmd="local_zones", data_list=domains_bulk)
print(o)
```
