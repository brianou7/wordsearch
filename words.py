import logging
import requests
import random
import threading

logger = logging.getLogger(__name__)


class InsertWordThread(threading.Thread):

    def __init__(self, word, board):
        super().__init__()
        self.word = word
        self.board = board

    def run(self):
        self.board.insert_x(self.word)


def generate_words(n: int = 5) -> list:
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    threads = []
    words = []

    def retrieve_from_api(words: list):
        length = random.randint(2, n)
        response = requests.get(f'https://random-word-api.herokuapp.com/word?lang=es&length={length}')
        word = str(response.json()[0]).upper()

        for char in special_chars:
            if char in word:
                word = word.replace(char, '')

        words.append(word)
        logger.debug(f'Thread completed: Word "{word}".')

    logger.info(f'Generating {n} words...\n')
    # Create and start threads to retrieve words from the API
    for i in range(n):
        thread = threading.Thread(target=retrieve_from_api, args=(words,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return words
