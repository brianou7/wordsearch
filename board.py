import logging
import random

logger = logging.getLogger(__name__)


class Board:

    def __init__(self, size: int=10) -> None:
        self.size = size
        self.unused_rows = [i for i in range(size)]
        self.content = [['.' for _ in range(size)] for _ in range(size)]
        self.solution = []
        self.words = []
        self.locations = {}

    def insert_x(self, word: str) -> None:
        row = random.choice(self.unused_rows)
        col = random.randint(0, self.size - len(word))
        self.unused_rows.remove(row)
        self.words.append(word)

        for i, letra in enumerate(word):
            self.content[row][col + i] = letra

        logger.debug(f'Word "{word}" inserted at row {row}, starting column {col}.')
        location = {'row': str(row), 'col': str(col), 'len': str(len(word)), 'dir': 'x'}
        self.locations.update({word: location})

    def fill(self) -> None:
        self.solution = [row.copy() for row in self.content]

        for i in range(self.size):
            for j in range(self.size):
                if self.content[i][j] == '.':
                    # ASCII Letters: A-Z
                    self.content[i][j] = chr(random.randint(65, 90))

    def mark_word(self, word:str, row: int, col: int, lenght: int, direction: str) -> None:
        square = chr(9632)  # Unicode for black square: '■'
        self.content[row][col:col + lenght] = [square for _ in range(lenght)]
        self.solution[row][col:col + lenght] = [square for _ in range(lenght)]
        self.words.remove(word)

    def find(self, word: str, key) -> bool:
        word = word.upper()

        if word in self.locations:
            location = self.locations[word]
            row, col, lenght, direction = key.split('-')
            result = row == location['row'] and \
                col == location['col'] and \
                lenght == location['len'] and direction == location['dir']

            if result:
                self.mark_word(word, int(row), int(col), int(lenght), direction)

            return result

        return False

    def _print_game(self, data):
        return '\n'.join([' '.join(row) for row in data])

    def print_conent(self):
        return self._print_game(self.content)

    def print_solution(self):
        return self._print_game(self.solution)
