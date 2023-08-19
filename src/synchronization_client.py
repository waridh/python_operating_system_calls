# This file contains the client object for a synchronization client

import socket_server.socclient as socclnt
import socket_server.packet_types as pac_t
import threading

class SyncClient(socclnt.SocketClient):
  def __init__(self, address, port, frame_size):
    super().__init__(address, port, frame_size)


  def run_syncclient(self): 
    # Running the client-server synchronization routine
    self.connect()
    self.send_command("HELLO")
