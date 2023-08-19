# This file is for syncing a number of servers and making them start at the same time
import socket_server.socserver as socserv
import socket_server.packet_types as pac_t
import threading

class SyncServer(socserv.ThreadedServer):
  def __init__(self, host, port, frame_size):
    # Need to initialize an
    super().__init__(host, port, frame_size)

  def sync_loop(self, num_clients):
    # sync_loop is the main loop for syncing server
    for i in range(0, num_clients):
      # trying to listen for just the specified number of clients
      client, address = self.sock.accept()
      threading.Thread(target= self.server_sync_thread, args= (client, address))   # Making service thread

  def server_sync_thread(self, client, address):
    # This is the thread function for synchronization.
    size = self.frame_size
    while True:
      data = pac_t.recv_msg_frame( client, address, size )
      if (data):
        print(data)
        # Sending confirmation packet
        pac_t.send_msg_frame(client, address, packet_types.MsgFrame("OK"))
      else:
        print("%s disconnected, closing connection" % (str(address)))
        client.close()
        print("socket closed")
        return

  def run_syncserver(self, num_clients):
    # Running the synchornization server
    print("Starting synchronization server")
    self.listen(num_clients)
    print("Starting listening loop")
    self.listen_loop()

if __name__ == "__main__":
  # testing purposes
  sync_server = SyncServer('', 4343, 4096)
