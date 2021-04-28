
import socket
import sys


try:
    TCP_IP= sys.argv[1]
except:
    print("Please provide the raspberry IP address")
    exit()

TCP_PORT = 5000
BUFFER_SIZE = 2056

f = open('stream.h264', 'wb')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP,TCP_PORT))
while True:
    data = sock.recv(BUFFER_SIZE)
    sys.stdout.buffer.write(data)
    print("Writing")
    
sock.close()
f.close()
