import socket
import traceback

'''Constants'''
IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
FORMAT = "UTF-8"
PLAYERS_CHECK = "Too Many Players"
OPTIONS = "You Have 3 Options"
GAME_OVER = "GAME OVER"
HELP = "Do You Want"
YOU_WON = "Well Done!!"
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
            while True:
                    welcome_msg = recv_msg(sock)
                    print(welcome_msg)
                    if PLAYERS_CHECK in welcome_msg:
                        sock.close()
                        return 0
                    while "Press 1" in (msg := recv_msg(sock)):
                        print(msg)
                        choice = ''
                        while not choice.isdigit() or choice not in ["0","1"]:
                            choice = input()
                        send_msg(sock, choice)
                        for i in range(3):
                            print(recv_msg(sock))
                            for j in range(4):
                                print(recv_msg(sock))
                            answer = ""
                            while not answer.isdigit() or answer not in ["1","2","3","4"]:
                                answer = input("\nEnter Your Answer: ")
                            send_msg(sock, answer)
                    while True:
                        if OPTIONS in msg:
                            print(msg)
                            stage = input("\nEnter Your Choice: ")
                            send_msg(sock, stage)
                            msg = recv_msg(sock)
                        else: break
                    msg2 = msg
                    while True:
                        try:
                            if GAME_OVER not in msg2 and YOU_WON not in msg2:
                                print(msg2)
                                msg2 = recv_msg(sock)
                                a_help = ""
                                answer = ""
                                while HELP in msg2:
                                    print(msg2)
                                    a_help = input("ENTER YES or NO: ")
                                    send_msg(sock, a_help)
                                    msg2 = recv_msg(sock)
                                    continue
                                if a_help.upper() == "YES":
                                    print(msg2)
                                    for _ in range(2):
                                        print(recv_msg(sock))
                                    answer = ''
                                    while answer not in ["1", "2"]:
                                        answer = input("\nEnter Your Answer")
                                    send_msg(sock, answer)
                                    msg2 = recv_msg(sock)
                                    continue
                                else:
                                    print(msg2)
                                    for _ in range(4):
                                        print(recv_msg(sock))
                                    while answer not in ["1", "2", "3", "4"]:
                                        answer = input("\nEnter Your Answer")
                                    send_msg(sock, answer)
                                    msg2 = recv_msg(sock)
                            else:
                                break
                        except:
                            raise
                    print(msg2)
                    print(recv_msg(sock))
                    answer = ""
                    while answer.upper() not in ["YES", "NO"]:
                        answer = input()
                    print("YES" == answer.upper())
                    if answer.upper() == "YES":
                        send_msg(answer)
                        continue
                    else:
                        send_msg(answer)
                        break
        except:
            traceback.print_exception()
        finally:
            sock.close()
            return 0
            
if __name__ == "__main__":
    main()
