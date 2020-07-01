from kiwoom.kiwoom import *
import sys
from PyQt5.QtWidgets import *


class UI_class():
    def __init__(self):
        print("UI_class입니다")

        self.app = QApplication(sys.argv)  # <- UI를 실행하기 위한 app
        # argv 리스트형태로 '파이썬 경로 '등이 담겨져 있음 ex) ['파이썬경로']

        self.kiwoom = kiwoom()  # <- 변수로 할당
        self.app.exec_()  # <- 이벤트루프를 실행해줌