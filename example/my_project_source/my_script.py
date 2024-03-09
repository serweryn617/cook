import socket

HOSTNAME = socket.gethostname()

print(f'my_script.py: Executing on {HOSTNAME}...')

with open('output', 'w') as f:
    f.write(f'Hello {HOSTNAME}!\n')

print('my_script.py: Finished!')