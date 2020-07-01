


class ParentDataHarvester:
    def __init__(self):
        super().__init__()
        self.Code_List_Aquirement()

    def Code_List_Aquirement(self):
        codeList001 = open('관심종목코드.txt')
        codeList002 = str(codeList001.readlines())
        print(codeList002)

