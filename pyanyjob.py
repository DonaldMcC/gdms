#/usr/bin/env python
# move this file to home directory, make executable and schedule on pythonanywhere with
# /home/yourusername/pyanyjob.py
# see https://help.pythonanywhere.com/pages/Web2pyScheduler/

import os
import socket
import subprocess
import sys
filename = os.path.abspath(__file__)  # we use this to generate a unique socket name

try:
    # we use a local socket as a lock.
    # it can only be bound once, and will be released if the process dies
    socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM).bind('\0' + filename)
except socket.error:
    print("Failed to acquire lock, task must already be running")
    sys.exit()

subprocess.call(["python", "web2py/web2py.py", "-K", "gdms"])