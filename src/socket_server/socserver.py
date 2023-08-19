import socket
import sys
import threading
import packet_types

class ThreadedServer(object):
  def __init__(self, host, port, frame_size):
    self.host = host
    self.port = port
    self.print_lock = threading.Lock()
    self.frame_size = frame_size    # Expected to be read-only
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP socket
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))                          # Binding to the selected port

  def safe_print(self, message):
    # Using mutex to prevent the print from being weird
    with self.print_lock:
      print(message)

  def listen(self, queue_size):
    # Make the socket listen
    self.sock.listen(queue_size)

  def listen_loop(self):
    # This method will start a polling loop that will accept connection requests
    # from the client
    while True:
      client, address = self.sock.accept()
      threading.Thread(target = self.listenToClient,args = (client,address)).start()

  def close_server(self):
    # For closing the server
    self.sock.close()

  def client_disconnected( self, clntsock, address ):
    # When a client disconnect, we run this function to notify and close
    # connection
    self.safe_print("The client: %s has disconnected.\n\tClosing socket now" %(str(address)))
    clntsock.close()

  def receive_command( self, clntsock, address ):
    # For the server to receive a command, and return the data
    # Need the socket and the address because threading
    try:
      data = packet_types.recv_msg_frame( clntsock, address, self.frame_size )
      if data:
        self.safe_print("Received <%s> packet from %s" % (str(data), str(address)))
        return data
      else:
        return False
    except Exception as e:
      self.safe_print("exception raised on receive_command.\n\tMessage: %s" %(str(e)))
      return False

  def send_command( self, clntsock, address, cmd):
    # Sending a command packet to the client. Also does the wrapping
    try:
      # Trying to send a packet
      packet_types.send_msg_frame(clntsock, address, packet_types.MsgFrame(cmd))
      self.safe_print("Sent the <%s> packet" % (cmd))
      return True
    except Exception as e:
      # just printing out error
      self.safe_print("failed to send packet.\n\tMessage: %s" % (str(e)))
      return False

  def receive_greeting(self, clntsock, address):
    # Establishing the connection with a client
    try:
      data = self.receive_command(clntsock, address)
      if (data.cmd == "HELLO"):
        # The client sent information
        self.send_command(clntsock, address, "HELLO")
        check = self.receive_command(clntsock, address)
        if (check.cmd == "OK"):
          self.safe_print("Established connection with client: %s" % (str(address)))
          return True
        else:
          raise ValueError("Client %s cannot receive packets from the server" % (str(address)))
      else:
        # Case when there is an error
        raise ValueError("Greeting failed with client %s" %(str(address)))
    except Exception as e:
      print("Exception raised on receive_greeting.\n\tMessage: %s" % (str(e)))
      self.client_disconnected(clntsock, address)
      return False


  def listenToClient(self, client, address):
    # This is the threading function. Will listen to the client
    size = self.frame_size
    self.receive_greeting(client, address)
    while True:
      data = packet_types.recv_msg_frame( client, address, size )
      if (data):
        self.safe_print(data)
        # Sending confirmation packet
        packet_types.send_msg_frame(client, address, packet_types.MsgFrame("OK"))
      else:
        self.safe_print("%s disconnected, closing connection" % (str(address)))
        client.close()
        self.safe_print("socket closed")
        return

if __name__ == "__main__":
  # For testing purposes
  print("Starting the socket server")
  socket_server = ThreadedServer('', 4242, 4096)
  socket_server.listen(5)
  print("Starting listening loop")
  socket_server.listen_loop()
