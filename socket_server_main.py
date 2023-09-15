import os
import sys
import re

# Work around for python imports
import_list = [ # Making a list for holding the directories. More scalable.
        'src'
        ]

# Making functions for the map program
make_path = lambda directory : os.path.join(os.path.dirname(
  os.path.abspath(__file__)), directory)
append_path = lambda path : sys.path.append(path)

# Using map to process the path combination.
get_import_path = list(map(make_path, import_list))
list(map(append_path, get_import_path))

# Importing the socket classes
import synchronization_client as sc
import synchronization_server as ss

#==============================================================================
#
# Argv utility and inputs
#
#==============================================================================

# argv_check = lambda flag_dict : 
"""
[argv_check] will crawl through the user argument and check the flags
"""

field_check = lambda stri : True if re.match(r'^-', stri) else False
"""
[field_check] returns True if the string [stri] starts with a -, else it will
return false. Used to find the user input flags.
"""

def flag_dict_cons_aux(args, flag_dict, idx):
  """
  [flag_dict_cons_aux(args, flag_dict, idx)] is the auxilery function to
  [flag_dict_cons], used for recursive solution.
  """
  if not args:
    # Empty list case (base case)
    return flag_dict
  elif (field_check(args[0])):
    # Case for when a flag is detected
    h, *t = args
    flag_dict[h] = idx
    return flag_dict_cons_aux(t, flag_dict, idx+1)
  else:
    # This is the case where it is just a value that doesn't need be logged
    _, *t = args
    return flag_dict_cons_aux(t, flag_dict, idx+1)

flag_dict_cons = lambda args : flag_dict_cons_aux(args, dict(), 0)
"""
[flag_dict_cons(args, flag_dict, idx)] is a function that constructs the dict
that holds information on the arguments that the user inputted.
"""

#==============================================================================
#
# Flag parsing
#
#==============================================================================

def get_arguments(args, flag_name, idx):
  """
  [get_arguments(args, flag_name, idx)] will get the corresponding argument to
  a certain flag. Not all flags will have arguments, so this function is
  necessary. The [args] is a list holding the command line arguments that the
  user inputted. The [flag_name] is the flag that we are trying to retrieve a
  value for, and [idx] is the index of the flag. Following convention, we want
  to retrieve the value stored at [idx + 1] in the [args] list.
  """
  if (idx + 1 >= len(args)):
    # Need to throw an exception, since the user must have misinputted
    raise ValueError("The user misinputted some arguments", flag_name)
  elif (field_check(args[idx+1])):
    # Case where there is a flag where an argument is expected. Also raise
    raise ValueError("The user misinputted some arguments", flag_name)
  else:
    return args[idx+1]

get_arg = lambda args, flag_dict, flag_name : get_arguments(
        args, flag_name, flag_dict[flag_name])

exists = lambda value, dictionary : True if value in dictionary else False
"""
[exists(value, dictionary)] just does checking if the value exists in a
dictionary.
"""

#==============================================================================
# Not Runnable cases
#==============================================================================

def error_case_checks(flag_dict):
  """
  [error_case_checks] is the controller program for user input.
  """
  if (not exists('-s', flag_dict)) and (not exists('-c', flag_dict)):
    # Program don't know client or server.
    raise ValueError("The user did not specify the mode of operation")
  elif (exists('-s', flag_dict) and exists('-c', flag_dict)):
    # Should not be both at the same time.
    raise ValueError("The user is using the program incorrectly.")
  else:
    return True

def client_check(flag_dict):
  """
  [client_check(flag_dict)] is a function that checks the [flag_dict] to see if
  the dictionary has all the flags and details that are needed to run the
  client program.
  """
  if ( (not(exists('-p', flag_dict))) or (not( exists('-a', flag_dict)))):
    return False
  else:
    return True

def server_check(flag_dict):
  """
  [client_check(flag_dict)] is a function that checks the [flag_dict] to see if
  the dictionary has all the flags and details that are needed to run the
  client program.
  """
  if ( (not(exists('-p', flag_dict))) ):
    return False
  else:
    return True

#==============================================================================
#
# Flow control
#
#==============================================================================
  
is_client = lambda flag_dict : (True) if (
    exists('-c', flag_dict) and client_check(flag_dict)
    ) else False

is_server = lambda flag_dict : (True) if (
    exists('-s', flag_dict) and server_check(flag_dict)
    ) else False

def run_program(flag_dict, args):
  """
  This function will lauch either the client or the server program based on
  the user input.
  """
  if is_server(flag_dict):
    # This is the server branch
    selected_port = int(get_arg(args, flag_dict, '-p'))
    print(
            "***\tStarting server program with the port of %d\t***"
            % (selected_port)
        )
    sync_server = ss.SyncServer(int(get_arg(args, flag_dict, '-p')))
    sync_server.run_syncserver(4)
  elif is_client(flag_dict):
    # This is the client branch
    print("*\tStarting client program")
    sync_client = sc.SyncClient(
            get_arg(
                args, flag_dict, '-a'
                ), int( get_arg(args, flag_dict, '-p')))
    sync_client.run_syncclient()

#==============================================================================
#
# Main function
#
#==============================================================================
def main():
  """
  [main()] is a function that reads the commandline arguments and choose whether
  the client or the server program will run. Does the control flow of the
  program.
  """
  flag_dict = flag_dict_cons(sys.argv)
  error_case_checks(flag_dict)  # Incorrect use handling.
  run_program(flag_dict, sys.argv)

if __name__ == "__main__":
  main()
