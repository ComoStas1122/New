import socket
import traceback

'''Constants'''
IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
FORMAT = "UTF-8"
'''Constants'''

def get_socket(*ADDR):
    '''
    This Function returns the connected socket to main
    :ADDR: tuple of (ip, port)
    :return: connected socket
    '''
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(ADDR)
    return sock


def recv_msg(sock: socket.socket) -> str:
    '''
    Just a function for easier message receiving..
    :sock: Actuall socket..
    :return: The message
    '''
    
    msg = ''
    while (b := sock.recv(1)) != b'\n':
        msg += b.decode(FORMAT)
    print(msg)
    return msg


def send_msg(sock, *msgs):
    '''
    Same as the server send_msg, this function sends the given msgs
    :sock: the actual socket which the transmition happen
    :msgs: the messages to send
    '''

    for msg in msgs:
        sock.send(msg.encode() + b'\n')


def main():
    '''
    This function is the main logic of the program..
    '''

    sock = None
    try:
        sock = get_socket(IP, PORT)
    except:
        traceback.print_exc()
        if sock is not None:
            sock.close()
        return
    else:
        try:
        welcome_msg = recv_msg(sock)
        if "Too Many Players" in welcome_msg:
            sock.close()
            return 0
        choice = ''
        while not choice.isdigit() or choice not in ["0","1"]:
            start_str = recv_msg(sock)
            choice = input()
        send_msg(sock, choice)
        msg = recv_msg(sock)
        

if __name__ == "__main__":
    main()
