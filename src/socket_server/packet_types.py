# This file will contain the data types that are used to communicate
# between the socket client and server.

from enum import Enum

class Msg_Type(Enum):
  # Creating enumeration for the frame class
  OK = 0
  QUIT = 1
  HELLO = 2
  MESSAGE = 3
  

class frame:
  def __init__(self, msg_type):
    # had to use a class to make an object for passing
    self.msg_type = msg_type
