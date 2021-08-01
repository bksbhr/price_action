import pandas as pd


class Order:
    def __init__(self):

        self.arr_column = ['EntryType', 'EntryTime', 'EntryPrice', 'ExitType', 'ExitTime', 'ExitPrice']
        self.arr_data = []
        self.df_log = pd.DataFrame(self.arr_data, columns=self.arr_column)

    def buy(self, price, time, p_type):

        if len(self.arr_data) == 0:
            self.arr_data.append('Buy_' + p_type)
            self.arr_data.append(time)
            self.arr_data.append(price)
            return
        if len(self.arr_data) > 2:
            self.arr_data.append('Buy_' + p_type)
            self.arr_data.append(time)
            self.arr_data.append(price)
            df = pd.DataFrame([self.arr_data], columns=self.arr_column)
            self.df_log = self.df_log.append(df, ignore_index=True)
            self.arr_data.clear()
            return self.df_log

    def sell(self, price, time, p_type):
        if len(self.arr_data) == 0:
            self.arr_data.append('Sell_' + p_type)
            self.arr_data.append(time)
            self.arr_data.append(price)
            return

        if len(self.arr_data) > 2:
            self.arr_data.append('Sell_' + p_type)
            self.arr_data.append(time)
            self.arr_data.append(price)
            df = pd.DataFrame([self.arr_data], columns=self.arr_column)
            self.df_log = self.df_log.append(df, ignore_index=True)
            self.arr_data.clear()
            return self.df_log

    def get_data(self):
        return self.df_log
