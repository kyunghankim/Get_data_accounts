from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
import pandas as pd
import sqlite3
import datetime
# 예측용 library들
import os
import tensorflow as tf
# import pandas as pd
import keras
import numpy as np
#from keras.layers import Embedding
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import math
from sklearn.metrics import mean_squared_error


#분봉 데이터 저장만 시도!!
class kiwoom2(QAxWidget):
    def __init__(self):  # <- 실행 되기 위한 정의
        super().__init__()

        print('Uiclass안에있는 키움클래스입니다')

        ### eventloop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        #self.detail_account_info_event_loop_2 = QEventLoop() #<-47강에서 루프합침
        self.calculator_event_loop = QEventLoop()
        #################

        ####스크린번호 모음
        self.screen_my_info = '2000'
        self.screen_calculation_stock = '4000'
        #######################

        ######### 변수모음
        self.account_num = None

        ##################

        ##### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ############################

        ####### 변수 모음
        self.not_account_stock_dict = {}
        self.account_stock_dict = {}
        ###################

        ######종목 분석 용
        self.calcul_data = []

        #####################

        self.get_ocx_instance()  # <- 키움에 레지스트리(KHOPENAPI.KHOpenAPICtrl.1)를 사용하겠다고
        # 말을 해야 함. 함수 get ocs instance를 정의해서 해결
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # <- 예수금 가져오는 것
        self.detail_account_mystock()  # <- 계좌평가 잔고 내역
        #self.not_concluded_account() # <- 미체결요청

        self.calculator_fnc2() #<- 종목 분석용 임시용으로 실행

    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 39강
        self.OnReceiveTrData.connect(self.trdata_slot)

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    # 37강 마지막 자동로그인(오른쪾아래 아이콘, 계좌비밀번호저장 아직 안함)

    def get_account_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)", "ACCNO")

        self.account_num = account_list.split(";")[0]

        print("나의계좌번호: %s", self.account_num)  # <-계좌번호가져오기

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

        #######/38강(로그인)까지

    ## 39강
    def detail_account_info(self):
        print("예수금 요청 부분")
        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", 0000)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String,String,int,String)", "예수금상세현황요청", "opw00001", "0",
                         "self.screen_my_info")  # <- 2000:screenNumber
        # screenNumber는 총 200개 까지 요청가능
        # self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  # <-loop실행: exec_와 exec는 같은 효과지만 미세가하게 다름(나중에공부)

    def detail_account_mystock(self, sPrevNext='0'):
        print("1.계좌평가잔고내역 요청")

        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String,String,int,String)",
                         "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        # self.detail_account_info_event_loop_2 = QEventLoop() <-이전 요청한게 있는데 다시 루프를 돌려서 오류발생!
        self.detail_account_info_event_loop.exec_()

        # 47강 미체결종목 (추가)요청
    #미체결종목 확인 주석처리!
    # def not_concluded_account(self, sPrevNext='0'):
    #     print("2.미체결종목 신호 확인용")
    #
    #     self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
    #     self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)",
    #                      "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)
    #
    #     self.detail_account_info_event_loop.exec_()

    def calculator_fnc2(self):
        """
        종목분석 실행용 함수
        :return:
        """
        code = '005930'
        # code_list = self.get_code_list_by_market("10")
        # print("코스닥 갯수 %s " % len(code_list))
        print("분봉용함수 calculator_fnc2")
        #print(self.code)
        self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
        # for idx, code in enumerate(code_list):
        #     self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)

        print("Samsung Code: %s is updating..." % code)
        self.minute_kiwoom_db(code=code)

    def minute_kiwoom_db(self, code=None, tick_interval=1, sPrevNext="0"):
        #tick_interval=1 로 설정해야 '1분'당 데이터로 들어옴
        print(code)
        QTest.qWait(4000)  #  딜레이 주기!
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", tick_interval)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", '0') #<- 수정주가부분 0이 기본값

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회", #<-분봉 데이터 request하기!
                        "opt10080", sPrevNext, self.screen_calculation_stock) #Tr서버로 전송

        self.calculator_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        """
        tr요청을 받는 구역/슬롯
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr코드
        :param sRecordName: 사용x
        :param sPrevNext: 다음페이지가 있는지
        :return:
        """
        # self.df = pd.DataFrame(columns= ['time', 'volume', 'info', 'open', 'high', 'low', 'adjusted'])
        # print('self.df확인용')
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % int(deposit))  # 41강

            self.use_money = int(deposit) * self.use_money_percent  # 예수금의 50%금액만 사용
            self.use_money = self.use_money / 4  # 50%금액의 1/4로 만!

            withdrawal = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액~ %s" % int(withdrawal))

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":

            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)",
                                               sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)",
                                                      sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%s): %s" % ('%', total_profit_loss_rate_result))

            # GetRepeatCnt: 멀티데이터 조회할때 쓰는것!
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                           sTrCode, sRQName, i, "종목명")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "종목번호")  # 종목앞에 거래소 정보가 알파벳으로!
                code = code.strip()[1:]  # strip으로 공백 지우고 1번 다음부터
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                  sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                             sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                              sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                 sTrCode, sRQName, i, "현재가")
                total_paid_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                    sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                     sTrCode, sRQName, i, "매매가능수량")
                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code: {}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity)
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_paid_price = int(total_paid_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_paid_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1

            print("계좌에 가지고있는 종목 %s" % len(self.account_stock_dict))
            print("계좌에 보유종목 카운트 %s" % cnt)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식분봉차트조회":

            daynow = datetime.datetime.now()
            # 월일이 10보다 작을 경우 0n으로 바꾸어줌
            year = daynow.year
            month = daynow.month
            day = daynow.day
            if month < 10:
                month = "0%s" % month
            if day < 10:
                day = "0%s" % day
            # 시분이 10보다 작을 경우 0x로 만들어줌
            hour = daynow.hour
            minute = daynow.minute
            if hour < 10:
                hour = "0%s" % hour
            if minute < 10:
                minute = "0%s" % minute

            rightnow = "%s%s%s%s%s" % (year, month, day, hour, minute)
            print("현재시간: %s" % rightnow)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("요청 데이터갯수: %s" % cnt)

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.split()
            print(code)
            # print("%s 분봉데이터 요청" % code)
            temp_df = pd.DataFrame(columns= ['time', 'volume', 'info', 'open', 'high', 'low', 'adjusted'])
            print(len(temp_df))
            for i in range(cnt):
                self.time = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "체결시간")
                self.volume = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "거래량")
                self.info = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "종목정보")
                self.open = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "시가")
                self.high = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "고가")
                self.low = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "저가")
                self.adjusted = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, i, "수정주가구분")

                # dictionary 만들어서 dataframe으로 만들고 concat하기, index가 0으로 채워짐
                for_df = pd.DataFrame({"time": [self.time], "volume": [self.volume],
                                        "info": [self.info], "open": [self.open],
                                        "high": [self.high], "low": [self.low],
                                        "adjusted": [self.adjusted]}, index=None)
                self.df = pd.concat([temp_df, for_df])
                print("self.df의 길이: %s" % len(self.df))

            print("concat확인용")
            # 저장된 900열 df의 index 따로 지정 set_index
            self.df.set_index('time')

            Dbpath = 'C:/Users/ilike/Database/'
            filename = 'samsung-minute'
            fileformat = '%s.csv' % rightnow

            # print(filename)
            # df2 = df.sort_values(by=['time'], axis=0, ascending=True)
            # df2.to_csv(Dbpath+filename + fileformat, sep=',',na_rep='NaN')
            print("저장확인용 %s 확인하기 string " % sPrevNext)


            if sPrevNext == "2":
                print("prevnext=2확인용")
                self.minute_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else: #업데이트 할 내용이 없을 때
                # Dbpath = 'C:/Users/ilike/Database/'
                # filename = 'samsung-minute-'
                # fileformat = '%s.csv' % rightnow
                # print(filename)
                # df2 = df.sort_values(by=['time'], axis=0, ascending=True)
                # df2.to_csv(Dbpath + filename + fileformat, sep=',', na_rep='NaN')

                self.calculator_event_loop.exit()