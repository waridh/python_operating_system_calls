# This file contains the client object for a synchronization client

import socclient as socclnt
import packet_types as pac_t
import threading

class SyncClient(socclnt.SocketClient):
  def __init__(self, address, port, frame_size):
    super().__init__(address, port, frame_size)

  def run_syncclient(self): 
    # Running the client-server synchronization routine
    self.connect()
    self.send_greeting()
    self.send_command("RDY")
    self.receive_command()
    self.receive_command()


if __name__ == "__main__":
  # Testing
  sync_client = SyncClient('localhost', 4343, 4096)
  sync_client.run_syncclient()
