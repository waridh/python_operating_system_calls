# This file contains a python client functionality
import socket
import packet_types

class SocketClient(object):
  def __init__(self, address, port, frame_size):
    self.server_address = address
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.frame_size = frame_size
    
  def connect(self):
    # connects to the specified ip address at the specified port
    try:
      self.sock.connect((self.server_address, self.port))
      print("Connected to the server: %s" % (str(self.server_address)))
    except Exception as e:
      print("There was an error connecting to the server.\n\tMessage: %s" %(e))

  def close_connection(self):
    self.sock.close()

  def disconnecting_server(self):
    # Function that will do debug printing and then end itself
    print("Disconnecting the server <%s>.\n\tClosing socket" % (str(self.server_address)))
    self.close_connection() 

  def receive_command( self ):
    # The client version of receiving a command
    try:
      data = packet_types.recv_msg_frame( self.sock, self.server_address, self.frame_size )
      if data:
        print("Received <%s> packet" %(str(data)))
        return data
      else:
        print("Received nothing")
        return False
    except Exception as e:
      print("exception raised on receive_command.\n\tMessage: %s" %(str(e)))
      return False

  def send_greeting(self):
    # Confirmation of established connection
    self.send_command("HELLO")
    response = self.receive_command()
    try:
      if (response.cmd == "HELLO"):
        # The server returned the expected res
        self.send_command("OK")
        print("Established connection with server: %s" %(str(self.server_address)))
        return True
      else:
        raise ValueError("Server %s sent incorrect response")
      return False
    except Exception as e:
      print("Error in the greeting protocol.\n\tMessage: %s" %(str(e)))
      self.disconnecting_server()
      return False

  def send_command(self, cmd):
    # send_command sends a command packet to the server
    packet_types.send_msg_frame(self.sock, self.server_address, packet_types.MsgFrame(cmd))
    print("sent cmd <%s>" %(cmd))


if __name__ == "__main__":
  # Testing the client server
  print("Starting Connection")
  socket_client = SocketClient('localhost', 4242, 4096)
  socket_client.connect()
  socket_client.send_greeting()
