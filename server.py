import socket
import traceback
import multiprocessing
import time
import re
from random import shuffle, randrange


'''Constants'''
IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
FORMAT = "UTF-8"
WELCOME_MSG = "WELCOME TO THE CHASE"
EXIT_MSG = "GOODBYE"
PRESS = "Press 1 to Play and 0 to Exit"
TOO_MANY_PLAYERS = "Too Many Players are Playing Right Now, Try Again Later..."
QUESTION = 5000
CHOOSE = "You Have 3 Options -> 1. Level 3 with {}\t2. Level 2 with {}\t3. Level 4 with {}"
GAME_OVER = "GAME OVER"
WANT_HELP = "Do You Want to Use Your Help?"
STATE = "Bitcoins -> {}\tHelping Hand -> {}\t Your Stage -> {} Chaser's Stage -> {}"
YOU_WON  = "Well Done!! You Won : {}"
PLAY_AGAIN = "DO You Want To Play Again?"
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


def extract_questions():
    with open("Questions.txt", "r") as f:
        lines = [line.rstrip() for line in f.readlines()]
        f.close()
    questions = {}
    question_re = re.compile(r"^(.*\?)")
    answers_re = re.compile(r"\(([-\w*,\s\w]+)\)")
    for question_phrase in lines:
        question = question_re.search(question_phrase).group(0)
        answers = answers_re.search(question_phrase).group(1).split(",")
        questions[question] = answers
    return questions

def shuffle_questions(questions):
    keys = list(questions.keys())
    shuffle(keys)
    return {key : questions[key] for key in keys}

def send_question(c_sock, question, answers, max_range = 4):
    print(max_range)
    send_msg(c_sock, question)
    enum = answers[:-1]
    if max_range == 2:
        enum = [answers[-1]]
        wrong = answers[0] if answers[0] != enum[0] else answers[1]
        enum.append(wrong)
        print(enum)
    for counter, answer in enumerate(enum):
        answer = f"{counter + 1}. {answer}"
        send_msg(c_sock, answer)
    answer = answers.index(enum[int(recv_msg(c_sock)) - 1]) + 1
    return answer


def chaser_answer(): 
    '''
    This Function Returns if the chaser one the 75% lottery
    :return: True if he did False if he didn't
    '''

    return randrange(1, 5) in [1, 2, 3]

    
    

def game(dict_help, count, lock, c_sock):
    '''
    This Function Handles the Game logic
    :c_sock: The socket that attached
    '''

    try:
        while True:
            dict_help[count][0] = 1
            print(dict_help[count], count)
            dict_help[count][1] = time.time()
            questions = extract_questions()
            correct = 0
            send_msg(c_sock, WELCOME_MSG)
            while not correct:
                questions = shuffle_questions(questions)
                send_msg(c_sock, PRESS)
                client_choice = recv_msg(c_sock)
                if client_choice == '0': 
                    send_msg(c_sock, EXIT_MSG)
                    return
                for (question, answers), _ in zip(questions.items(), range(3)):
                    answer = send_question(c_sock, question, answers)
                    if answers[int(answer) - 1] == answers[-1]:
                        correct += 1
                dict_help[count][1] = time.time()
            user_money = correct * QUESTION
            chaser_stage = 0
            while True:
                send_msg(c_sock, CHOOSE.format(user_money, user_money*2, user_money//2))
                client_stage = recv_msg(c_sock)
                if client_stage == "1":
                    client_stage = 3
                elif client_stage == "2":
                    client_stage = 2
                    user_money *= 2
                elif client_stage == "3":
                    user_money /= 2
                    client_stage = 4
                else:
                    continue
                break

            helping_hand = 1
            q_counter = 3
            while True:
                max_range = 4
                if chaser_stage == client_stage:
                    send_msg(c_sock, GAME_OVER)
                    send_msg(c_sock, PLAY_AGAIN)
                    break
                elif client_stage == 7:
                    send_msg(c_sock, YOU_WON.format(user_money))
                    send_msg(c_sock, PLAY_AGAIN)
                    break
                send_msg(c_sock, STATE.format(user_money, helping_hand, client_stage, chaser_stage))
                if helping_hand:
                    send_msg(c_sock, WANT_HELP)
                    while (ans := recv_msg(c_sock).upper()) not in ["YES", "NO"]:
                        send_msg(c_sock, WANT_HELP)
                        continue
                    if ans == "YES":
                        helping_hand = 0
                        max_range = 2
                answers = questions[(question := list(questions.keys())[q_counter])]
                print(answers, question)
                answer = send_question(c_sock, question, answers, max_range)
                if answers[int(answer)] == answers[-1]:
                    client_stage += 1
                if chaser_answer():
                    chaser_stage += 1
                q_counter += 1
            if recv_msg(c_sock).upper() == "YES":
                continue
            else:
                break
    except:
        traceback.print_exc()
    finally:
        c_sock.close()
        dict_help[count][0] = 0
        if lock.acquire():
            lock.release()
        return


def clean_up(conns, dict_help, lock, keys):
    try:
        lock.acquire()
        print("1")
        closed_keys = [key for key in dict_help if dict_help[key] == 0 or
                       time.time() - dict_help[key][1] > 10]
        print(keys, dict_help, closed_keys)
        for key in closed_keys:
            keys.append(key)
            del dict_help[key]
            if not conns[key][2]._closed:
                conns[key][2].close()
            conns[key][1].terminate()
            del conns[key]
        
    except:
        traceback.print_exc()
    finally:
        print(conns, dict_help)
        lock.release()
            

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

    dict_help = multiprocessing.Manager().dict()
    conns = {}
    lock = multiprocessing.Lock()
    keys = [1, 2, 3]
    while True:
        c_sock, addr = serv_sock.accept()
        clean_up(conns, dict_help, lock, keys)
        if len(conns) == 3:
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
        print(f"{c_sock} is connected, connection number {len(conns) + 1}")
        dict_help[(key := keys.pop(0))] = [1, time.time()]
        p = multiprocessing.Process(target = game, args = (dict_help, key, lock, c_sock))
        conns[key] = (addr, p, c_sock)
        p.start()


if __name__ == "__main__":
    main()

