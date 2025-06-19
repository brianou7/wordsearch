import socket
import os
import pickle
import time

from exceptions import Break, Continue
from utils import send_message

HOST = 'localhost'
PORT = 12345

def print_words(message):
    words = message['words']

    if words:
        print('\nWords to search:', ', '.join(words))
    else:
        print('\nCongratulations! You found all the words!')

def start(s: socket.socket, request: dict):
    size = input('Please type a size: ').lower()
    request.update({'size': int(size)})
    message = send_message(s, request)

    print('============= WordSearch =============')
    print(message['board'])
    print_words(message)

def words(s: socket.socket, request: dict):
    print_words(send_message(s, request))

def word(s: socket.socket, request: dict):
    word = input('Please type the word: ').lower()
    location = input('Please type where it starts (row,col): ')
    row, col = location.split(',')
    row = int(row.strip()) - 1
    col = int(col.strip()) - 1
    request.update({'word': word, 'row': row, 'col': col})
    message = send_message(s, request)
    result = message.get('result', False)

    if result:
        print(f'You\'re right! Word "{word}" found!\n')
        print(message['board'])
    else:
        print(f'Sorry, "{word.upper()}" is not at this location.\n')

    print_words(message)

    if not message['words']:
        raise Break()

def solve(s: socket.socket, request: dict):
    message = send_message(s, request)
    print('=============  Solution  =============')
    print(message['board'])
    input('\nPlease type Enter to continue: ')
    raise Break()

def stop(s: socket.socket, request: dict):
    print('Finishing game...') 
    s.sendall(pickle.dumps(request))
    s.close()
    raise Break()

ACTIONS = {
    'start': start,
    'words': words,
    'word': word,
    'solve': solve,
    'stop': stop
}

def end_state(action, start_at):
    end_at = time.time()
    duration = round(end_at - start_at, 2)
    print(f'\nGame finished. Time: {duration}s.\n')

    if action == 'solve':
        print(f'Restarting in...', end='')

        for i in range(3, 0, -1):
            print(f' {i}..', end='.')
            # Non-blocking timer: print countdown without blocking the UI
            for _ in range(10):
                time.sleep(0.1)

        print('\n\n' + '-' * 60)
        _ = os.system('clear')
        main()

def main():
    start_at = time.time()
    menu = '''Welcome to Wordsearch Game!!!

    Actions:
    - start: Start the game.
    - word: Search for a word in the board.
    - words: Show the list of words to find.
    - solve: Show the solution.
    - stop: Exit the game.
    '''
    print(menu)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            try:
                action = input('Action: ').lower()
                request = {'action': action}

                if action not in ACTIONS:
                    print('Invalid action. Please try again.\n')
                    continue

                ACTIONS[action](s, request)
            except Break:
                break
            except Continue:
                print('Invalid action on this state. Please try again.\n')
                continue

    end_state(action, start_at)

if __name__ == "__main__":
    main()
