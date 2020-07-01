# 앞으로 실행은 이걸로만 할거임
from ui.ui import UI_class

class Main():
    def __init__(self):
        print("실행할 메인 클래스")
        UI_class()

if __name__ =="__main__":
    Main()