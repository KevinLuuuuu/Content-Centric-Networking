import socket
import json
import threading
from socket import SHUT_RDWR
import time

with open('./input.txt') as f:
  data = json.load(f)
print(data)

network = data["network"]
input = data["input"]
#print(network)
#print(input)

server=[]
thread=[]
bind_ip = "127.0.0.1"
bind_port = 2001
#client_handler = threading.Thread()

for i in range(len(network)):
  server_temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_temp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_temp.bind((bind_ip, bind_port))
  #server_temp.listen(5)
  server.append(server_temp)
  bind_port+=1

done = 0

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print ("Received: %s" % request)
    client_socket.send("ACK!".encode())
    client_socket.close()
    
def server_thread(dest_num):
  try:
    while True:
      server[dest_num].listen(5)
      client, addr = server[dest_num].accept()
      #print ("Acepted connection from: %s:%d" % (addr[0],addr[1]))
      client_handler = threading.Thread(target=handle_client, args=(client,))
      client_handler.start()
  finally:
    return

for i in range(len(input)):
  for j in range(len(input[i])):
    dest = int(input[i][j][1])
    sender = int(input[i][j][0])
    if(network[sender][1][0]!=dest and network[sender][1][1]!=dest):
      print("unreachable")
    else:
      thread_temp = threading.Thread(target=server_thread, args=(dest,))
      thread_temp.start()
      time.sleep(1)

      #thread.append(thread_temp)
      data = input[i][j][2]
      #print(server[1])
      #print(data)
      print(dest)

      server[sender].connect((bind_ip, 2001+dest))
      time.sleep(1)
      server[sender].send(data.encode())

      response = server[sender].recv(4096)
      print (string(response))

      server[sender].shutdown(SHUT_RDWR)
      server[sender].close()
      server[dest].close()

      time.sleep(1)

      server[sender] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server[sender].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      server[sender].bind((bind_ip, 2001+i))

      server[dest] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server[dest].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      server[dest].bind((bind_ip, 2001+dest))

      time.sleep(1)
      #print(server[1])
