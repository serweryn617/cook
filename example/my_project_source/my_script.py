import socket
import sys
import time

HOSTNAME = socket.gethostname()

print(f'[1/2] {__file__}: Executing on {HOSTNAME}...', flush=True)

with open('output', 'w') as f:
    f.write(f'Hello {HOSTNAME}!\n')

sys.stderr.write("Some error 2!\n")

time.sleep(2)

print(f'[2/2] {__file__}: Finished!', flush=True)
