# This file is for syncing a number of servers and making them start at the same time
import socserver as socserv
import packet_types as pac_t
import threading
import select

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

  def check_num_rdy(self):
    """
    This method will return True when the number of ready clients match the specified
    number
    """
    with self.rdy_lock:
      if (self.num_clients == self.rdy_clients):
        return True
      else: return False

  def sync_loop(self):
    # sync_loop is the main loop for syncing server
    self.safe_print("Initializing the barrier")
    self.sync_bar = threading.Barrier( self.num_clients )   # main + all thread
    self.safe_print("Barrier created for %d clients" % (self.num_clients))
    while True:
      # trying to listen for just the specified number of clients
      # Not going to use select until needing to implement keyboard input as well
      self.safe_print("Waiting for client")
      client, address = self.sock.accept()
      # Making service thread
      threading.Thread(target= self.server_sync_thread, args= (client, address)).start()   

  def server_sync_thread(self, client, address):
    """
    server_sync_thread(client, address)

    This is the thread function that controls the interaction with a client.

    States:
      0 - Base state. No trigger waits or anything yet
    """
    state_counter = 0   # I have a mutable state
    self.receive_greeting(client, address)  # Confirm connection
    # better polling method than just a blocking receive
    while True:
      data = pac_t.MsgFrame("DEFAULT")
      try:
        ready_to_read, ready_to_write, in_err = \
            select.select([client,], [client,], [], 1)
      except Exception as e:
        print("caught exception\n\tMessage: %s" % (str(e)))
        # Going to officially disconnect the client server
        self.decrement_rdy_clients(address)
        self.client_disconnected(client, address)
      if (len(ready_to_read) > 0):
        # The client sent something
        self.safe_print("Client <%s> sending packet" %(str(address)))
        data = self.receive_command(client, address)
        if (data):
          state_counter = self.sync_state_machine(client, address, data, state_counter)
        else:
          self.client_disconnected(client, address)
          return  # Closed the socket and end the thread
      elif (len(ready_to_write) > 0):
        # The client is ready to receive something
        # self.safe_print("Client <%s> ready to receive" %(str(address)))
        state_counter = self.sync_state_machine(client, address, data, state_counter)
      else:
        self.safe_print("Pass")
        pass

  def state_one(self, client, address):
    # Client has confirmed sync ready
    self.increment_rdy_clients(address)
    self.send_command(client, address, "OK")

  def send_trigger(self, client, address):
    # Send a packet to the client that the trigger occurred
    """
    Needs better handling for when the clients may randomly disconnect
    """
    self.sync_bar.wait()
    self.send_command(client, address, "SYNC_TRIGGER")

  def sync_state_machine(self, client, address, data, state_counter):
    """
    sync_state_machine is a finite state machine method that will choose the
    action of the program based on the current state and the data input.
    """
    self.safe_print("State machine\n\tstate: %d\n\tinput: %s" %(state_counter, str(data)))
    # This function is used to to control the thread state based on the input
    if (data.cmd == "DEFAULT"):
      # Higher level branching so that we don't have to check all the conditions
      if (state_counter == 1):
        # Need to check if the correct number of clients have connected
        if (self.check_num_rdy):
          # Means that all the clients are ready
          return 2
        else:
          return 1
      elif (state_counter == 2):
        # Time to wait on the barrier and send trigger
        self.send_trigger(client, address)
        return 3
      else: return state_counter  # Ensure that the return is correct
        
    elif ((data.cmd == "RDY") and (state_counter == 0)):
      self.state_one(client, address)
      return 1
    else:
      return state_counter
    
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
