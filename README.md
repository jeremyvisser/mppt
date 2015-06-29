BlueSolar MPPT Communication Library
Copyright (C) 2015 Ace Internet Services Pty Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Usage:

```
./mppt.py <host> <port> [--no-checksum]
```

See also:

```
cacti.py (for insertion into Cacti)
```

Note that BlueSolar MPPT devices are not network-enabled.  To
network-enable a device, use a MikroTik router to access the serial
port and expose as a TCP port.

One way to do this is to use a TTL-to-USB serial cable.  Note that the
cable supplied by Victron is not supported by the MikroTik.  However,
other chipsets such as FTDI work with the BlueSolar controller as well as
MikroTik RouterOS.

The output can be collected in Cacti rather easily by using cacti.py. It
outputs data in the format required by Cacti Data Input Methods.

First, check that the script works:

	./cacti.py 192.168.88.1 26001

Output should look like:

	LOAD:ON H19:95 VPV:19.36 ERR:0 FW:116 [etc. etc.]

Add a Data Input Method within Cacti, with the path to the script,
with hostname and port input fields, and output fields referring to
what you want to graph.
