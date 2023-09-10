import os
import sys

# Work around for python imports
import_list = [ # Making a list for holding the directories. More scalable.
        'socket_server'
        ]

# Making functions for the map program
make_path = lambda directory : os.path.join(os.path.dirname(
  os.path.abspath(__file__)), directory)
append_path = lambda path : sys.path.append(path)

# Using map to process the path combination.
get_import_path = list(map(make_path, import_list))
list(map(append_path, get_import_path))

# Importing the socket classes
import synchronization_client
import synchronization_server



if __name__ == "__main__":
  print("hello world")
