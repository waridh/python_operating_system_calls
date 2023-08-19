# This file contains a python client functionality
import socket
import packet_types

class SocketClient(object):
  def __init__(self, address, port):
    self.server_address = address
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
  def connect(self):
    # connects to the specified ip address at the specified port
    try:
      self.sock.connect((self.server_address, self.port))
    except Exception as e:
      print("There was an error connecting to the server.\n\tMessage: %s" %(e))

  def close_connection(self):
    self.sock.close()


if __name__ == "__main__":
  # Testing the client server
