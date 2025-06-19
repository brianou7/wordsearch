import asyncio
import logging
import os
import pickle
import random
import socket
import threading
import time
import websockets

from board import Board
from words import InsertWordThread, generate_words


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

HOST = 'localhost'
PORT = 12345
WS_PORT = 8765

clients = {}

def start_game(client, size):
    words = generate_words(n=random.randint(size//2, size))
    logger.info('----------------------------------------------------------')
    board = Board(size=size)
    threads = []
    logger.info(f'Creating game board {size}x{size} and {len(words)} words')
    logger.info(f'Words: {words}')

    for word in words:
        thread = InsertWordThread(word, board)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    logger.debug('----------------------------------------------------------')
    board.fill()
    solution = board.print_solution()
    client.update({'board': board})
    logger.debug(f'Showing solution board... \n{solution}')
    logger.debug('----------------------------------------------------------')
    
    game = board.print_conent()
    logger.debug(f'Showing game board... \n{game}')

    return {'board': game, 'words': words}

def show(clients):
    logger.info('----------------------------------------------------------')

    if clients:
        logger.info('Clients:')

        for n, client in enumerate(clients.keys(), start=1):
            logger.info(f'{n} - {client}')
    else:
        logger.info('Clients: No active clients.')

def finish_game(clients, addr, extra):
    if addr in clients:
        response = {'time': time.time() - clients[addr].get('start_at')}
        response.update(extra)
        logger.info(f'Client {addr} has stopped game.')
        clients.pop(addr, None)
        show(clients)
        return response

    return {'error': 'No active game for this client'}

def tcp_server():
    global clients
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            logger.info('Wordsearch server is running...')
            logger.info(f'Server started on {HOST}:{PORT}')
            logger.info('Type Ctrl/Cmd + C to stop the server.\n')
            logger.info('Server waiting for client connections...')

            while True:
                conn, addr = s.accept()
                threading.Thread(target=handler, args=(conn, addr, clients)).start()
    except KeyboardInterrupt:
        logger.info('Server stopped by user.')

def handler(conn, addr, clients):
    with conn:
        logger.info(f'Connection from {addr}')
        logger.info('----------------------------------------------------------')

        while True:
            try:
                data = conn.recv(4096)

                if not data:
                    continue

                try:
                    message = pickle.loads(data)
                    action = message.get('action')

                    if action == 'start':
                        client = {'start_at': time.time()}
                        response = start_game(client, message.get('size'))
                        clients.update({addr: client})
                        show(clients)
                    elif action == 'words':
                        response = {'words': clients[addr]['board'].words}
                    elif action == 'word':
                        board = clients[addr]['board']
                        word = message.get('word')
                        row, col = message.get('row'), message.get('col')
                        key = '-'.join([str(row), str(col), str(len(word)), 'x'])
                        response = {
                            'result': board.find(word, key),
                            'board': board.print_conent(),
                            'words': board.words
                        }
                    elif action == 'stop':
                        response = finish_game(clients, addr)
                        import pdb; pdb.set_trace()
                    elif action == 'solve':
                        solution = {'board': clients[addr]['board'].print_solution()}
                        response = finish_game(clients, addr, solution)
                    else:
                        response = {'error': 'Unknown action'}
                except:
                    response = {'error': 'Unknown error'}

                conn.sendall(pickle.dumps(response))
            except ConnectionResetError:
                logger.error(f'Client {addr} disconnected.')
                clients.pop(addr, None)
                show(clients)
                continue
            except Exception as e:
                error_msg = {'error': str(e)}
                conn.sendall(pickle.dumps(error_msg))

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, HOST, WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    tcp_server()
    # tcp_thread = threading.Thread(target=tcp_server, daemon=True)

    # tcp_thread = threading.Thread(target=tcp_server)
    # tcp_thread.start()
    # asyncio.run(main())
