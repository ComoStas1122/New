import socket
import traceback
import multiprocessing

'''Constants'''
IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
FORMAT = "UTF-8"
WELCOME_MSG = "WELCOME TO THE CHASE"
EXIT_MSG = "GOODBYE"
PRESS = "Press 1 to Play and 0 to Exit"
TOO_MANY_PLAYERS = "Too Many Players are Playing Right Now, Try Again Later..."
'''Constants'''

def send_msg(sock, *msgs):
    '''
    This function send messages in socket..
    :sock: the socket
    :msgs: messages to send
    '''
    print(msgs)
    for msg in msgs:
        sock.send(msg.encode() + b"\n")


def get_server_socket(*ADDR):
    '''
    Function that creates and returns the server's socket
    :ADDR: Which (IP, PORT) bind to
    :return: the socket
    '''
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(ADDR)
    sock.listen()
    return sock


def recv_msg(sock):
    '''
    Function that receives a message until a new line
    :sock: The transmition socket
    :return: the message
    '''

    msg = ''
    while (b := sock.recv(1)) != b'\n':
        msg += b.decode(FORMAT)
    return msg
    

def game(c_sock):
    '''
    This Function Handles the Game logic
    :c_sock: The socket that attached
    '''

    c_sock.settimeout(10)
    send_msg(c_sock, WELCOME_MSG, PRESS)
    try:
        client_choice = recv_msg(c_sock)
    except:
        print("Too Much Time waiting for an answer")
        c_sock.shutdown(2)
        c_sock.close()
        return
    if client_choice == '0':
        send_msg(c_sock, EXIT_MSG)
        c_sock.close()
        return


def main():
    '''
    This is the main server logic function
    '''

    serv_sock = None
    try:
        serv_sock = get_server_socket(IP, PORT)
    except:
        traceback.print_exc()
        if serv_sock is not None:
            serv_sock.close()
        return


    conns = {}
    while True:
        c_sock, addr = serv_sock.accept()
        delete = []
        if len(conns) >= 3:
            p = multiprocessing.Process(target = send_msg, args = (c_sock, TOO_MANY_PLAYERS))
            p.start()
            p.join()
            try:
                print(len(conns))
                c_sock.close()
                p.terminate()
            except:
                traceback.print_exc()
            finally:
                continue
        print(f"{addr} is connected, connection number {len(conns) + 1}")
        p = multiprocessing.Process(target = game, args = (c_sock, ))
        conns[p] = (addr, c_sock)
        p.start()
            
                
if __name__ == "__main__":
    main()

