# Python Synchronization Server

Quick python multithreaded socket server implementation to demonstrate my understanding of some operating sytem concepts.

## Usage

To run the synchronization socket server, follow these steps.

1. Run the following command: `python3 socket_server_main.py`

## User input

Here is a table that contains the flags and the description for them.

| Flag | Description | Parameter |
| --- | --- | --- |
| -s | Indicates that the program is running as a server. | Requires the -p flag |
| -c | Indicates that the program is running as a client. | Requires the -p and the -a flag to be filled|
| -p | The port flag. After this flag, input the port that is being utilized. | Takes in an integer between 0 and 65535. |
| -a | This address flag. Only applicable to the client mode of the program. | Takes in a DNS serviceble address (read as string) |


## TODO

- Improve the client side process, so that it is more clear to readers
- Add the handling case when the client turned itself off, the server should reflect that as well
- Make the interface layer for the program (Command line arguments)
