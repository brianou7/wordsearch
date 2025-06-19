import socket
import sys
import time

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from utils import send_message


HOST = 'localhost'
PORT = 12345


class LetterLabel(QLabel):

    def __init__(self, letter, row, col, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.letter = letter
        self.row = row
        self.col = col
        self.setText(letter)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black; font-size: 20px; background: gray;")
        self.setFixedSize(40, 40)
        self.selected = False

    def mousePressEvent(self, event):
        self.selected = not self.selected

        if self.selected:
            self.setStyleSheet("border: 2px solid red; font-size: 20px; background: yellow; color: black;")
        else:
            self.setStyleSheet("border: 1px solid black; font-size: 20px; background: gray;")


class Ui_MainWindow:

    def __init__(self, s, board, words):
        self.socket = s
        self.board = board
        self.words = words

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(parent=self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(60, 10, 551, 531))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")

        # 5x5 wordsearch grid
        self.gridWidget = QtWidgets.QWidget(parent=self.frame)
        self.gridWidget.setGeometry(QtCore.QRect(100, 100, 220, 220))
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setSpacing(2)
        self.gridWidget.setObjectName("gridWidget")

        # Example 5x5 grid
        self.grid_letters = [
            ['C', 'A', 'T', 'S', 'Y'],
            ['O', 'D', 'O', 'G', 'Z'],
            ['W', 'O', 'R', 'D', 'S'],
            ['P', 'Y', 'T', 'H', 'O'],
            ['N', 'E', 'S', 'T', 'S'],
        ]
        self.labels = []
        for i in range(5):
            row_labels = []
            for j in range(5):
                label = LetterLabel(self.grid_letters[i][j], i, j)
                self.gridLayout.addWidget(label, i, j)
                row_labels.append(label)
            self.labels.append(row_labels)

        self.pushButton = QtWidgets.QPushButton(parent=self.frame)
        self.pushButton.setGeometry(QtCore.QRect(60, 420, 100, 32))
        self.pushButton.setObjectName("Click 1")
        self.pushButton.clicked.connect(lambda: print('click'))
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(220, 420, 100, 32))
        self.pushButton_2.setObjectName("Click 2")
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.frame)
        self.pushButton_3.setGeometry(QtCore.QRect(370, 420, 100, 32))
        self.pushButton_3.setObjectName("Click 3")
        self.label = QtWidgets.QLabel(parent=self.frame)
        self.label.setStyleSheet("font-size: 24px;")
        self.label.setGeometry(QtCore.QRect(200, 10, 200, 30))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 780, 60))
        self.label_2.setObjectName("label2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Wordsearch Game"))
        self.pushButton.setText(_translate("MainWindow", "Validate"))
        self.pushButton_2.setText(_translate("MainWindow", "Solve"))
        self.pushButton_3.setText(_translate("MainWindow", "Stop"))
        self.label.setText(_translate("MainWindow", "Wordsearch Game"))
        self.label_2.setText(_translate("MainWindow", f"Words: {', '.join(self.words)}"))

    def show(self):
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        self.setupUi(MainWindow)
        MainWindow.show()
        # self.label_2.adjustSize()
        sys.exit(app.exec())

def main():
    start_at = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = ({'action': 'start', 'size': 30})
        message = send_message(s, request)
        board = [row.split(' ') for row in message['board'].split('\n')]
        ui = Ui_MainWindow(s=s, board=board, words=message['words'])
        ui.show()

        # while True:
        #     pass
        #     try:
        #         request = {'action': action}
        #     except Break:
        #         break
        #     except Continue:
        #         print('Invalid action on this state. Please try again.\n')
        #         continue

if __name__ == "__main__":
    main()
