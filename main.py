import statistics
from order import Order
import pandas as pd

stock_df = pd.read_csv('GAIL_5m.csv')


# return all candles of current day according position
def cur_day(pos):
    return stock_df.iloc[pos * 75:(pos + 1) * 75]


# return all candles of previous day according position
def prv_day(pos):
    pos = pos - 1
    return stock_df.iloc[pos * 75:(pos + 1) * 75]


def find_res_sup(cr_df):
    df = cr_df
    low = 500
    high = 0
    index = None
    # print(df.iloc[0].Open, df.iloc[74].Close)
    if df.iloc[0].Open > df.iloc[74].Close:
        for i in range(1, 73):
            if df.iloc[i].Open < df.iloc[i].Close and df.iloc[i].Volume > df.iloc[i - 1].Volume:
                if df.iloc[i].Low < low:
                    low = df.iloc[i].Low if df.iloc[i].Low < low else low
                    index = df.iloc[i]
    if df.iloc[0].Open == df.iloc[74].Close:
        index = df.iloc[74]
    if df.iloc[0].Open < df.iloc[74].Close:

        for i in range(1, 73):
            if df.iloc[i].Open > df.iloc[i].Close and df.iloc[i].Volume > df.iloc[i - 1].Volume:

                if df.iloc[i].High > high:
                    high = df.iloc[i].High if df.iloc[i].High > high else high
                    index = df.iloc[i]

    return index


def trade_start(res_candle, cr_day):
    lowest_resistance = cr_day.iloc[0].Low + cr_day.iloc[0].Low
    higher_support = 0
    res_conformation = False
    sup_conformation = False
    break_point = 0
    target = 2.5
    sl = 1.5
    sl_r = 2
    tolrence = 0
    wait_mode = False
    try_to_sell = False
    try_to_buy = False
    is_sell = False
    is_buy = False
    res = statistics.mean([int(res_candle.High), int(res_candle.Low)])
    trade_buy = True


    for i in range(len(cr_day)):
        trade_buy = True if cr_day.iloc[i].Low > res else False
        # update lower support
        if cr_day.iloc[i].Open > cr_day.iloc[i].Close:
            lowest_resistance = cr_day.iloc[i].Open if cr_day.iloc[i].Open < lowest_resistance else lowest_resistance
        if cr_day.iloc[i].Open < cr_day.iloc[i].Close:
            higher_support = cr_day.iloc[i].Open if cr_day.iloc[i].Open > higher_support else higher_support

        # find the resistance conformation candle
        if trade_buy \
                and cr_day.iloc[i].Open > cr_day.iloc[i].Close \
                and cr_day.iloc[i].Volume > cr_day.iloc[i - 1].Volume \
                and not res_conformation \
                and not wait_mode \
                and lowest_resistance < cr_day.iloc[i].Low:
            res_conformation = True

            # print('resistance conformation candle:', cr_day.iloc[i])
            continue

        # find the support conformation candle(green candle)
        if not trade_buy \
                and cr_day.iloc[i].Open < cr_day.iloc[i].Close \
                and cr_day.iloc[i].Volume > cr_day.iloc[i - 1].Volume \
                and not sup_conformation \
                and not wait_mode \
                and higher_support > cr_day.iloc[i].High:
            sup_conformation = True
            # print('support conformation candle:', cr_day.iloc[i])

            continue

        # selling trapping candle
        if trade_buy \
                and cr_day.iloc[i].Open > cr_day.iloc[i].Close \
                and cr_day.iloc[i].Volume > cr_day.iloc[i - 1].Volume \
                and res_conformation \
                and not wait_mode \
                and lowest_resistance < cr_day.iloc[i].Low:
                # and cr_day.iloc[0].High + 2.5 > cr_day.iloc[i].High:
            break_point = cr_day.iloc[i].High + tolrence

            try_to_sell = False
            try_to_buy = True
            # print('selling trapping candle:', cr_day.iloc[i])
            continue

        # buying trapping candle
        if not trade_buy \
                and cr_day.iloc[i].Open < cr_day.iloc[i].Close \
                and cr_day.iloc[i].Volume > cr_day.iloc[i - 1].Volume \
                and sup_conformation \
                and not wait_mode \
                and higher_support > cr_day.iloc[i].High:
                # and cr_day.iloc[0].High - 2.5 < cr_day.iloc[i].Low:
            break_point = cr_day.iloc[i].Low - tolrence

            try_to_buy = False
            try_to_sell = True
            # print('buying trapping candle:', cr_day.iloc[i])
            continue
        if not wait_mode and i >= 48:
            # reset()
            break

        #     if break hit place sell order
        if try_to_sell and not wait_mode and cr_day.iloc[i].Low < break_point:
            wait_mode = True
            is_sell = True
            # print("sell punch")
            order.sell(break_point, cr_day.iloc[i].Date, 'Entry')
            continue

        #     if break hit place buy order
        if try_to_buy and not wait_mode and cr_day.iloc[i].High > break_point:
            wait_mode = True
            is_buy = True
            # print("buy punch")
            order.buy(break_point, cr_day.iloc[i].Date, 'Entry')
            continue

        if i == 73:
            # reset()
            break
        if wait_mode:
            if is_sell and cr_day.iloc[i].Low < break_point - target:
                order.buy(break_point - target, cr_day.iloc[i].Date, 'Target')
                wait_mode = False
                break
            if is_sell and cr_day.iloc[i].High > break_point + sl:
                order.buy(break_point + sl, cr_day.iloc[i].Date, 'SL')
                wait_mode = False
                break
            if i == 72 and is_sell:
                order.buy(cr_day.iloc[i].Close, cr_day.iloc[i].Date, 'SQ')
                wait_mode = False
                # reset()
                break
            if is_buy and cr_day.iloc[i].High > break_point + target:
                order.sell(break_point + target, cr_day.iloc[i].Date, 'Target')
                wait_mode = False
                break
            if is_buy and cr_day.iloc[i].Low < break_point - sl:
                order.sell(break_point - sl, cr_day.iloc[i].Date, 'SL')
                wait_mode = False
                break
            if i == 72 and is_buy:
                order.sell(cr_day.iloc[i].Close, cr_day.iloc[i].Date, 'SQ')
                wait_mode = False
                # reset()
                break


def start():
    test = 4
    all_day = int(len(stock_df) / 75)
    for i in range(all_day):
        if i > 0:
            res_candle = find_res_sup(prv_day(i))
            # print(res_candle.Open)
            # print(res_candle)
            # print(i)
            # print(res_candle)
            cr_day = cur_day(i)
            trade_start(res_candle, cr_day)


def print_log():
    df = order.get_data()
    sq = 0
    b_sl = 0
    s_sl = 0
    target = 0
    for i in range(len(df)):
        if df.iloc[i].ExitType == 'Buy_SL':
            b_sl = b_sl + 1
        if df.iloc[i].ExitType == 'Sell_SL':
            s_sl = s_sl + 1
        if df.iloc[i].ExitType == 'Sell_Target' or df.iloc[i].ExitType == 'Buy_Target':
            target = target + 1
        if df.iloc[i].ExitType == 'Buy_SQ' or df.iloc[i].ExitType == 'Sell_SQ':
            sq = sq + 1
    try:
        df.to_csv('log_GAIL.csv')
    except:
        print("Warnning.......  change the name of log csv file")


    print('Total Trades:-', len(df))
    print('Total BUY SL:-', b_sl)
    print('Total SELL SL:-', s_sl)
    print('Total SQ:-', sq)
    print('Total Targets:-', target)


if __name__ == '__main__':
    order = Order()

    start()
    print_log()
