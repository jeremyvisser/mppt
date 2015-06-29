#!/usr/bin/env python
"""
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
	./mppt.py <host> <port> [--no-checksum]

See also:
	cacti.py (for insertion into Cacti)

Note that BlueSolar MPPT devices are not network-enabled.  To
network-enable a device, use a MikroTik router to access the serial
port and expose as a TCP port.

One way to do this is to use a TTL-to-USB serial cable.  Note that the
cable supplied by Victron is not supported by the MikroTik.  However,
other chipsets such as FTDI work with the BlueSolar controller as well as
MikroTik RouterOS.
"""

import sys
import socket

class MPPT(object):
	"""	BlueSolar MPPT Communications Class
		usage:
			m = MPPT(('192.168.88.1', 26001))
			s = m.status()
			print s
			# output:
			LOAD	ON
			H19	94
			VPV	19.59
			ERR	0
			FW	116
			I	3.12
			H21	114
			IL	0.5
			PID	41026
			H20	8
			H23	70
			H22	22
			HSDS	7
			SER#	XXXXXXXXXXX
			V	14.39
			CS	4
			PPV	53

	"""

	def __init__(self, target, timeout=5, retries=3, retry_delay=1.0, validate_checksum=True):
		"""	Constructor: opens connection to BlueSolar MPPT controller.
			usage for TCP socket: MPPT(('192.168.88.1', 26001))
			usage for serial:     MPPT('/dev/ttyS0')
		"""

		self.retries = retries
		self.retry_delay = retry_delay

		if isinstance(target, (list, tuple)): # socket connection
			for res in socket.getaddrinfo(target[0], target[1], socket.AF_UNSPEC, socket.SOCK_STREAM):
				af, socktype, proto, canonname, sa = res
				try:
					s = socket.socket(af, socktype, proto)
				except socket.error, msg:
					s = None
					continue
				try:
					s.connect(sa)
				except socket.error, msg:
					s.close()
					s = None
					continue
				break
			if s is None:
				raise Exception('could not open socket')

			s.settimeout(timeout)

			self.comm = s.makefile() # returns file-like object

		elif isinstance(target, basestring): # file I/O based (tty) connection
			s = open(target, 'r+b')
			if s is None:
				raise Exception('could not open serial port')
			self.comm = s

		else:
			raise Exception('could not understand what you want to connect to')

	def status(self):
		"""	Reads the MPPT status in ASCII mode
			
			Because it's a serial connection, corrupted lines
			are tolerated by skipping them and retrying until
			a checksum-passing series of lines is found.
		"""
		failures_remaining = 10

		while failures_remaining > 0:
			failures_remaining -= 1

			# rolling checksum
			checksum = 0
			
			status = {}

			while True:
				line = self.comm.readline().strip()

				# handling a corrupted line, in case we start listening to the stream mid-line
				if '\t' not in line:
					break

				# if it doesn't split cleanly into exactly two fields, skip
				try:
					key, value = line.split('\t')
				except ValueError:
					break

				if key == 'PID':
					status[key] = int(value, 16) # convert from hex string
				elif key in (
						'V',
						'VPV',
						'I',
						'IL',):
					status[key] = float(value) / 1000 # convert from milli
				elif key in (
						'FW',
						'PPV',
						'CS',
						'ERR',
						'H19',
						'H20',
						'H21',
						'H22',
						'H23',
						'HSDS',):
					status[key] = int(value) # convert from decimal str to int
				elif key == 'Checksum':
					pass
				else:
					status[key] = value

				checksum += ord('\r') + ord('\n')
				for char in line:
					checksum += ord(char)

				if key == 'Checksum':
					if checksum % 256 == 0:
						return status
					else:
						if validate_checksum:
							break
						else:
							if failures_remaining < 2:
								return status

		raise Exception('ran out of parse attempts')

if __name__ == '__main__':
	sys.argv.pop(0) # argv[0] is the script name

	host = sys.argv.pop(0)
	port = sys.argv.pop(0)
	validate_checksum = True

	try:
		while True:
			arg = sys.argv.pop(0)
			if arg == '--no-checksum':
				validate_checksum = False
	except IndexError:
		pass

	m = MPPT((host, port), validate_checksum=validate_checksum)
	status = m.status()
	for key, value in status.iteritems():
		print('%s\t%s' % (key, value))

