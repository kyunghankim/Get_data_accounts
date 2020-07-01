import sqlite3
import pandas as pd

class StockDb(object):

    # 싱글톤 패턴
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            return cls._instance
        return cls._instance


    def __init__(self):
        self.open_Db()

    # DB를 오픈한다.
    def open_Db(self):
        self.con = sqlite3.connect("./kosdaq_leverage.db")
        self.cursor = self.con.cursor()


    def create_StockDb(self):
        self.cursor.execute("CREATE TABLE kosdaq_leve(date text unique, high int, low int);")
        self.cursor.execute("CREATE TABLE kosdaq_start(date text unique, start int);")
        self.cursor.execute("CREATE TABLE kosdaq_leve_day(date text unique, start int, end int);")


    def create_OrderDb(self):
        self.cursor.execute("CREATE TABLE buy(date text, buy_price int, buy_reason text, buy_id integer primary key autoincrement);")
        self.cursor.execute("CREATE TABLE sell(date text, sell_price int, sell_reason text, sell_id integer primary key autoincrement references buy(buy_id));")
        self.cursor.execute("CREATE TABLE optimize_profit(mean_level int, price_limit int, profit int);")

    def insert_Leve(self,day,high, low):
        self.cursor.execute("insert into kosdaq_leve values(?,?,?);",(day,high,low))

    def insert_Start(self,day,start):
        self.cursor.execute("insert into kosdaq_start values(?,?);",(day,start))

    def insert_Leve_Day(self,day,start,end):
        self.cursor.execute("insert into kosdaq_leve_day values(?,?,?);",(day,start, end))

    def insert_Buy(self,day,price,reason):
        self.cursor.execute("insert into buy (date,buy_price,buy_reason) values(?,?,?);",(day,price,reason))

    def insert_Sell(self,day,price,reason):
        self.cursor.execute("insert into sell (date,sell_price,sell_reason) values(?,?,?);", (day,price, reason))

    def insert_Profit(self, mean_level, limit, profit):
        self.cursor.execute("insert into optimize_profit values(?,?,?);",(*********,**********))

    def select_MinuteData(self,day):
        data = pd.read_sql("SELECT * FROM kosdaq_leve where date like \'" + day + "%\' order by date;", self.con, index_col=None)
        return data

    def select_DailyStart(self,day):
        data = pd.read_sql("SELECT * FROM kosdaq_start where date like \'"+day+"%\' order by date;", self.con, index_col=None)
        return data

    def select_Buy(self,day):
        day = day[0:8]
        data = pd.read_sql("SELECT * FROM buy where date like \'"+day+"%\';",self.con, index_col=None)
        return data

    def select_Sell(self,day):
        day = day[0:8]
        data = pd.read_sql("SELECT * FROM sell where date like \'" + day + "%\';", self.con, index_col=None)
        return data

    def select_Date(self, start, end):
        data = pd.read_sql("SELECT date FROM kosdaq_start where date >= \'" + start + "000000\' and date <= \'"+end+"090000\' order by date;", self.con, index_col=None)
        return data

    def delete_Buy_Sell(self):
        self.cursor.execute("DELETE FROM sell;")
        self.cursor.execute("DELETE FROM buy;")
        self.cursor.execute("DELETE FROM sqlite_sequence;")
        self.commit()

    def select_Daily_Data(self,start,end):
        data = pd.read_sql("SELECT * FROM kosdaq_leve_day where date >= \'" + start + "\' and date <= \'"+ end +"\';", self.con, index_col=None)
        return data

    def select_Optimize_Data(self):
        data = pd.read_sql("SELECT * FROM optimize_profit;", self.con, index_col=None)
        return data

    def commit(self):
        self.con.commit()

if __name__ == "__main__":
    db = StockDb()
    db.create_StockDb()
    db.create_OrderDb()