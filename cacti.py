#!/usr/bin/env python

"""	MPPT output in Cacti format

Outputs data in the format required by Cacti Data Input Methods.

First, check that the script works:

	./cacti.py 192.168.88.1 26001

Output should look like:

	LOAD:ON H19:95 VPV:19.36 ERR:0 FW:116 [etc. etc.]

Add a Data Input Method within Cacti, with the path to the script,
with hostname and port input fields, and output fields referring to
what you want to graph.
"""

import sys
import mppt

try:
	host, port = sys.argv[1], sys.argv[2]
except IndexError:
	print('usage: %s <host> <port>' % sys.argv[0])
	sys.exit(1)

m = mppt.MPPT((host, port))

status = m.status()

for key, value in status.iteritems():
	print '%s:%s' % (key, value),

