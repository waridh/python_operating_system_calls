# This file will contain the data types that are used to communicate
# between the socket client and server.

import sys
import pickle

class MsgFrame:
  # This class is the massage frame for tcp communications
  def __init__(self, cmd="OK"):
    self.cmd = cmd
  def __str__(self): return self.cmd

# I am going to include the functions to send this frame here
def send_msg_frame(sock, address, packet):
  # sends a message frame
  try:
    sock.send(pickle.dumps(packet))
    return True
  except:
    return False

def unpickle_frame(data):
  # Function for unpicking a frame
  try:
    unpickled_data = pickle.loads(data)
    if unpickled_data:
      return unpickled_data
    else:
      raise ValueError('Unable to unpickle data')
  except Exception as e:
    print("unpickling failed\n\tMessage: %s" %(str(e)))
    return False

def recv_msg_frame(sock, address, size):
  # Recv a message frame of the format in this file
  try:
    data = sock.recv(size)
    if data:
      return unpickle_frame(data)
    else:
      raise ValueError('socket disconnected')
  except Exception as e:
    print("exception occurred on recv_msg_frame\n\tMessage: %s" %(str(e)))
    return False

if __name__ == "__main__":
  # Result of experiment is that we do not have a constant size item
  # when using pickle
  print(sys.getsizeof(pickle.dumps(MsgFrame("OK"))))
  print(sys.getsizeof(pickle.dumps(MsgFrame("QUIT"))))
