# This file is for syncing a number of servers and making them start at the same time
import socserver as socserv
import packet_types as pac_t
import threading
import select
import sys 

class SyncServer(socserv.ThreadedServer):
  def __init__(self, host, port, frame_size):
    # Need to initialize an
    super().__init__(host, port, frame_size)
    self.num_clients = 0
    self.rdy_clients = 0
    self.rdy_lock = threading.Lock()  # lock for updating status
    self.program_ended = False        # only the main can change
    self.end_lock = threading.Lock()  # mutex anyways in case
    self.service_threads = []         # list for holding the thread objects

  def quit_program(self):
    """
    Quits the program, including cleaninng up the threads
    """
    with self.end_lock:   # Update the program end flag
      self.program_ended = True
    self.safe_print("Quitting program,\nCollecting threads")
    for thread in self.service_threads:
      self.safe_print("\tjoining thread <%s>" % (str(thread.ident)))
      thread.join()
    self.close_server()
    sys.exit()

  def ready_monitor(self):
    # This is general monitoring. Do not put this function where the function already
    # grabbed the rdy_lock
    with self.rdy_lock:
      self.safe_print("\t%d/%d clients are ready" % (self.rdy_clients, self.num_clients))

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

  def sync_disconnect(self, client, address):
    """
    [sync_disconnect] is a method that will disconnect the client on the server side
    and then decrement the sync ready counter
    """
    self.client_disconnected(client, address)
    self.decrement_rdy_clients(address)

  def check_num_rdy(self):
    """
    This method will return True when the number of ready clients match the specified
    number
    """
    with self.rdy_lock:
      if (self.num_clients == self.rdy_clients):
        return True
      else:
        return False

  # Section for server terminal inputs
  def server_commands(self, cmd):
    """
    [server_commands] is the control flow method for commands sent to the server
    terminal
    """
    if (cmd == "quit"):
      # The user wants to quit the program on the server
      self.quit_program()

  def sync_loop(self):
    # sync_loop is the main loop for syncing server
    self.safe_print("Initializing the barrier")
    self.sync_bar = threading.Barrier( self.num_clients )   # main + all thread
    self.safe_print("Barrier created for %d clients" % (self.num_clients))
    input_list = [self.sock.fileno(), sys.stdin.fileno()]
    while True:
      try:
        ready_to_read, _, _ = \
            select.select(input_list, [], [], 1)
      except Exception as e:
        print("caught exception\n\tMessage: %s" % (str(e)))
      # trying to listen for just the specified number of clients
      # Not going to use select until needing to implement keyboard input as well
      for x in ready_to_read:
        if x == self.sock.fileno():
          client, address = self.sock.accept()
          # Making service thread
          service_thread = threading.Thread( \
              target= self.server_sync_thread, \
              args= (client, address))
          self.service_threads.append(service_thread)
          service_thread.start()
          self.safe_print("Accepted connection with client: %s" %(str(address)))
        if x == sys.stdin.fileno():
          term_in = sys.stdin.readline()[:-1] # Reading entire line but remove \n
          self.server_commands(term_in)

  # Service thread stuff

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
      if (self.program_ended):
        # When the program has ended, we need to start the ending proc
        self.send_command(client, address, "CANCEL")
        return
      else:
        try:
          ready_to_read, ready_to_write, _ = \
              select.select([client,], [client,], [], 100)
        except Exception as e:
          self.safe_print("caught exception\n\tMessage: %s" % (str(e)))
          # Going to officially disconnect the client server
          self.sync_disconnect(client, address)
        if (len(ready_to_read) > 0):
          # The client sent something
          self.safe_print("Client <%s> sending packet" %(str(address)))
          data = self.receive_command(client, address)
          if (data):
            state_counter = self.sync_state_machine(client, address, data, state_counter)
          else:
            self.sync_disconnect(client, address)
            return  # Closed the socket and end the thread
        elif (len(ready_to_write) > 0):
          # The client is ready to receive something
          # self.safe_print("Client <%s> ready to receive" %(str(address)))
          state_counter = self.sync_state_machine(client, address, pac_t.MsgFrame("DEFAULT"), state_counter)
        else:
          self.safe_print("Pass")
          pass

  def state_one(self, client, address):
    # Client has confirmed sync ready
    self.increment_rdy_clients(address)
    self.send_command(client, address, "OK")

  def state_three(self, client, address):
    """
    [state_three] is a method that finalizes the server interaction after

    """

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
    # self.safe_print("State machine\n\tstate: %d\n\tinput: %s" %(state_counter, str(data)))
    # This function is used to to control the thread state based on the input
    if (data.cmd == "DEFAULT"):
      # Higher level branching so that we don't have to check all the conditions
      if (state_counter == 1):
        # Need to check if the correct number of clients have connected
        if (self.check_num_rdy()):
          # Means that all the clients are ready move on to the next state
          self.ready_monitor()
          return 2
        else:
          return state_counter
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
