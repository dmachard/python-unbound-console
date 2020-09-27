# Python remote control for unbound server

![Build](https://github.com/dmachard/unbound-remotecontrol/workflows/Build/badge.svg) ![Testing](https://github.com/dmachard/unbound-remotecontrol/workflows/Testing/badge.svg) ![Unbound](https://byob.yarr.is/dmachard/unbound-remotecontrol/unbound) ![Python](https://byob.yarr.is/dmachard/unbound-remotecontrol/python)

![License](https://badgen.net/badge/License/MIT/yellow?icon=github) ![Pypi](https://github.com/dmachard/unbound-remotecontrol/workflows/PyPI/badge.svg)

## Table of contents
* [Installation](#installation)
* [Remote Control on Unbound](#remote-control-on-unbound)
* [Execute command](#execute-command)

## Installation

This module can be installed from [pypi](https://pypi.org/project/unbound_remotecontrol/) website

```python
pip install unbound_remotecontrol
```

## Remote Control on Unbound

Before to use this utility. You must activate the remote control on your unbound server.
See [config file](https://github.com/dmachard/unbound-remotecontrol/blob/master/tests/unbound_remotecontrol_tls.conf) example. 

### Execute command

You can execute commands with the function `send_command`. See [nlnetlabs documentations](https://www.nlnetlabs.nl/documentation/unbound/unbound-control/) for the full list of available commands.

- Import the module in your code

```python
from unbound_remotecontrol import RemoteControl
```

- Configure the remote control client

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
