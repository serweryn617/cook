import socket

HOSTNAME = socket.gethostname()

print(f'Executing script on {HOSTNAME}...')

with open('output', 'w') as f:
    f.write(f'Hello {HOSTNAME}!\n')

print('Script finished!')