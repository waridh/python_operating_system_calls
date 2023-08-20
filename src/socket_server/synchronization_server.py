# This file is for syncing a number of servers and making them start at the same time
import socserver as socserv
import packet_types as pac_t
import threading

class SyncServer(socserv.ThreadedServer):
  def __init__(self, host, port, frame_size):
    # Need to initialize an
    super().__init__(host, port, frame_size)
    self.num_clients = 0
    self.rdy_clients = 0
    self.rdy_lock = threading.Lock()  # lock for updating status

  def increment_rdy_clients(self, address):
    # Incrementing the list of ready clients
    try:
      with self.rdy_lock:
        self.rdy_clients += 1
        self.safe_print("client: %s has been counted\n\t%d/%d clients ready" % (
          address, self.rdy_clients, self.num_clients))
      return True
    except Exception as e:
      self.safe_print("caught exception on increment_rdy_clients\n\tMessage: %s" %(str(e)))
      return False

  def decrement_rdy_clients(self, address):
    # Decrement the list of ready clients
    try:
      with self.rdy_lock:
        self.rdy_clients -= 1
        self.safe_print("client: %s has been removed\n\t%d/%d clients ready" % (
          address, self.rdy_clients, self.num_clients))
      return True
    except Exception as e:
      self.safe_print("caught exception on increment_rdy_clients\n\tMessage: %s" %(str(e)))
      return False

  def sync_loop(self):
    # sync_loop is the main loop for syncing server
    self.safe_print("Initializing the barrier")
    self.sync_bar = threading.Barrier( self.num_clients )   # main + all thread
    self.safe_print("Barrier created for %d clients" % (self.num_clients))
    while True:
      # trying to listen for just the specified number of clients
      self.safe_print("Waiting for client")
      client, address = self.sock.accept()
      threading.Thread(target= self.server_sync_thread, args= (client, address)).start()   
      # Making service thread

  def server_sync_thread(self, client, address):
    state_counter = 0
    # This is the thread function for synchronization.
    self.receive_greeting(client, address)
    while True:
      data = self.receive_command(client, address)
      if (not data):
        # No data received. Likely disconnected
        self.client_disconnected(client, address)
        self.decrement_rdy_clients(address) # Decrementing the count
        return
      else:
        # Move into flow control
        state_counter = self.sync_state_machine(client, address, data, state_counter)

  def state_one(self, client, address):
    # Client has confirmed sync ready
    self.increment_rdy_clients(address)
    self.send_command(client, address, "OK")

  def send_trigger(self, client, address):
    # Send a packet to the client that the trigger occurred
    """
    Something
    """
    self.send_command(client, address, "SYNC_TRIGGER")

  def sync_state_machine(self, client, address, data, state_counter):
    # This function is used to to control the thread state based on the input
    if ((data.cmd == "RDY") and (state_counter == 0)):
      self.state_one(client, address)
      self.sync_bar.wait()  # Waiting for all the clients to be ready
      self.send_trigger(client, address)
      return 1
    
  def run_syncserver(self, num_clients):
    self.num_clients = num_clients
    # Running the synchornization server
    print("Starting synchronization server for %d clients" % (num_clients))
    self.listen(num_clients)
    print("Starting listening loop")
    self.sync_loop()

if __name__ == "__main__":
  # testing purposes
  sync_server = SyncServer('', 4343, 4096)
  sync_server.run_syncserver(2)
