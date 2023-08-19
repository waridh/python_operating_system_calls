import socket
import threading
import packet_types

class ThreadedServer(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP socket
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))                          # Binding to the selected port

    def listen(self, int: queue_size = 5):
      # Make the socket listen
      self.sock.listen(queue_size)

    def listen_loop(self):
      # This method will start a polling loop that will accept connection requests from the client
      while True:
        client, address = self.sock.accept()
        client.settimeout(60)
        threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
      # This is the threading function. Will listen to the client
      size = 1024
      while True:
        try:
          data = client.recv(size)
          if data:
            # Set the response to echo back the recieved data 
            response = data
            client.send(response)
          else:
            raise error('Client disconnected')
        except:
          client.close()
          return False

if __name__ == "__main__":
  while True:
    port_num = input("Port? ")
        try:
          port_num = int(port_num)
          break
        except ValueError:
          pass

  ThreadedServer('',port_num).listen()
