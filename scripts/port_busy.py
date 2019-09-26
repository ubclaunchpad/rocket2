"""
Check to see if a port is busy on the machine you are running on.

Usage: python3 scripts/port_busy.py <port number>

Used in place of `nmap` for automatically checking if the port used for local
instances of DynamoDB is in use.

Exits with 0 if the port is in use.
Exits with 1 if there is an issue connecting with the port you provided.
Exits with 2 if the 'port' you provided couldn't be converted to an integer.
Exits with 3 if you didn't provide exactly 1 argument.
Exits with 4 if the port is not already in use.
"""
import socket
import errno
import sys

if len(sys.argv) != 2:
    print(f'{sys.argv[0]} <port number>')
    sys.exit(3)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(('localhost', int(sys.argv[1])))

    sys.exit(4)
except socket.error as e:
    if e.errno == errno.EADDRINUSE:
        # Address in use
        sys.exit(0)
    else:
        # Some other thing
        sys.exit(1)
except TypeError:
    # Couldn't convert string to int
    sys.exit(2)
