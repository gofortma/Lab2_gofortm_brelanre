# this is the server 
# So... now you know how to make sockets and use them in C... or Java, or some other language.  Using the language of your choice (it must be a base language, nothing like Python Flask or Ruby on Rails, etc.  If you're not sure, just ask!  But this assignment may be done in Python, Java, C, etc.), you are to make a server that handles two kinds of requests:

# iWant
# uTake
# That is, the client now merely takes commands on the command-line, and then the client uses its socket connection to the server to send the command as-is to the server.

# NOTE: Below, you are given things to output in the case of an error.  You can use whatever error messages you want, feel free to get creative.

# The server is to parse the command.  The only commands accepted currently are iWant and uTake.  If neither of these is the command given to the server, the server should respond to the client with a message "That just ain't right!" and move on to the next command.  This response can be used for any number of generic errors found in the command.


# iWant
# On the client side, whenever a user types "iWant xyz" where xyz is the name of a file, the string is sent to the server without modification.  The server must then parse the command and if the command is well-formed AND the file exists, sends the requested file.  If the file does not exist, the server should send the string "Failure:  What you talkin' bout Willis?  I ain't seen that file anywhere!"  For any other type of malformed request, you can send a generic error message like the one above.  

# On the client side, you should ask what directory the user wishes to place the file before the file transfer begins.  If the user leaves that empty (by just hitting enter), then you should save the incoming file in a default folder as described below.

# uTake 
# On the client side, whenever a user types "uTake xyz" where xyz is the name of a file, the client must validate if the file exists on the client-side (printing an error message if not), the string is sent to the server without modification if the file exists on the client-side informing the server that it should accept a file named xyz.  The client can either send the file WITH the message (if the server is ready for it), or better, you can choose some protocol where the server informs the client that it is ready to receive the file after it has parsed the command successfully.  In either case, the client is to send the server the file named xyz.

# Directory Structure
# Please keep the client and server programs in a separate directory!  If you fail to do this, sending and receiving files (especially when using localhost) will get messy.

# Please keep all client-side code in a directory named something like 'Lab2/client' where the files received from the server should default to 'Lab2/client/received_files'  

# Please keep all server-side code in a directory named something like 'Lab2/server' where the files kept to send to the client are kept in 'Lab2/server/store'.  Files received from the client may be stored here by default or in another folder named something like 'Lab2/server/received_files'.

# Application Protocol
# You will DEFINITELY need to develop your own application protocol for this lab!  When the user types "iWant file.pdf" there should be several points of communication between the client and server.  You will probably want to communicate between the client and server things like the file size, where it is located or where it shoudl go, etc.  In other words, you probably won't be able to do everything in just a simple send-the-command-and-get-a-file interaction.

# When the file is finished being sent/received, you should maintain the connection, or start a new one (transparently to the user!).  This means in the same run of one client/server program, you should be able to send and receive multiple files.

# Note, the commands are meant to be typed only on the client so that iWant asks for a file from the server and uTake requests to send a file to the server.

# You can specify the directory structure in the commands or in a separate follow-up command.  For example, you can do one of the following two:

# > iWant directory1/directory2/directory3/filexyz.txt
# Or:

# > iWant filexyz.txt
#   From Server: not found in default directory, please provide the directory
# > directory1/directory2/directory3
# Note that the directory structure will work with absolute paths (/root/home/...) or relative (../someOtherDirectory/...).  The first above will reduce your overall back-and-forth message sending between server and client but the second one may be easier depending on the protocol you develop.

from math import ceil
import socket
import sys
import os

BUFFER_SIZE = 4096


def server_program():
    # get the hostname
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)
    print("Host name: " + str(host))
    print("Host IP: " + str(host_ip))
    # host = 'localhost'
    if(len(sys.argv) != 2):
       print("Usage: python server.py <port_number>")
       sys.exit()
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('', port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)


    while True: # keep looping looking for new clients when previous closes
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        current_path = os.getcwd()
        print("Current path: " + str(current_path))
        while True:

            

            command = conn.recv(BUFFER_SIZE).decode()
            print("command: ", command)
            if command == "exit":
                break
            elif command == "iWant":
                filename = conn.recv(BUFFER_SIZE).decode()
                print("iWant")
                print("filename: ", filename)
                # check if its in FileStore
                if not os.path.isfile(os.path.join(current_path + "/FileStore", filename)):
                    print("file is not file")
                    conn.send("-1".encode())
                elif not os.path.exists(os.path.join(current_path +"/FileStore", filename)):
                    print("file does not exist")
                    conn.send("-1".encode())

                else:
                    print("file exists")
                    filesize = os.path.getsize(os.path.join(current_path + "/FileStore", filename))
                    conn.send(str(filesize).encode())
                    with open(os.path.join(current_path + "/FileStore", filename), "rb") as f:
                        while True:
                            print("reading file")
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            conn.send(bytes_read)
                    print("Sent " + str(filesize) + " bytes of " + filename)
            elif command == "uTake":
                print("uTake")
                directory = conn.recv(BUFFER_SIZE).decode()
                
                if(directory == "default"):
                    directory = current_path + "/ReceivedFiles"
                elif(directory == "."):
                    directory = current_path
                if not os.path.exists(directory):
                    print("not found in directory, please provide the directory")
                    conn.send("-1".encode())
                elif not os.path.isdir(directory):
                    print("not a directory")
                    conn.send("-1".encode())
                else:
                    print("Directory valid")
                    conn.send("0".encode())
                    size = conn.recv(BUFFER_SIZE).decode()
                    print("size: ", size)
                    if(size == -1):
                        print("file does not exist")
                    else:
                        print("Recieving file...")
                        size = int(size)
                        recieve_call = ceil(size/BUFFER_SIZE)
                        print("recieve call: ", recieve_call)
                        filename = conn.recv(BUFFER_SIZE).decode()
                        with open(os.path.join(directory, filename), "wb") as f:
                            print("writing file")
                            for _ in range(recieve_call):
                                bytes_read = conn.recv(BUFFER_SIZE)
                                f.write(bytes_read)
                        f.close()
                        print("Recieved " + str(size) + " bytes of " + filename)

        conn.close()  # close the connection


if __name__ == '__main__':
    server_program()

