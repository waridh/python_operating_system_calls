# This file contains the client object for a synchronization client

import socclient as socclnt
import packet_types as pac_t
import threading
import select
import sys

class SyncClient(socclnt.SocketClient):
  def __init__(self, address, port, frame_size):
    super().__init__(address, port, frame_size)

  def ready_for_sync(self):
    # Send the ready packet to the server to keep count
    self.send_command("RDY")
    response = self.receive_command()
    if (response.cmd == "OK"):
      return True
    else:
      raise ValueError("Incorrect response for ready sync")
    return False

  def wait_for_start_cmd(self):
    # Waiting the for the go! signal from the server
    command = self.receive_command()
    if (command.cmd == "SYNC_TRIGGER"):
      # TODO: Make the action better for the use
      print("SYNCHRONIZATION TRIGGER RECEIVED")
      return
    else:
      raise ValueError("Incorrect response", command.cmd)

  def client_loop(self):
    """
    [client_loop] is the method that contains the main loop that controls
    flow
    """
    io_list = [self.sock.fileno(), sys.stdin.fileno()]
    while True:
      # Using select to multiplex between socket and stdin
      try:
        ready_to_read, ready_to_write, _ = \
            select.select(io_list, [self.sock.fileno()], [], 1)
      except Exception as e:
        print("caught exception\n\tMessage: %s" % (str(e)))
      for x in ready_to_read:
        if (x == self.sock.fileno()):
          # server sent something
          pass
        elif (x == sys.stdin.fileno()):
          # User typed something in
          pass
      for x in ready_to_write:
        if (x == self.sock.fileno()):
          # the server wants to client to send something
          pass

  def run_syncclient(self): 
    # Running the client-server synchronization routine
    self.connect()
    self.send_greeting()
    try:
      self.ready_for_sync()
      self.wait_for_start_cmd()
    except Exception as e:
      print("caught exception\n\tMessage: %s" % (str(e)))


if __name__ == "__main__":
  # Testing
  sync_client = SyncClient('localhost', 4343, 4096)
  sync_client.run_syncclient()
