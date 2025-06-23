import matplotlib.pyplot as plt
from flask import Flask, render_template, request, g, redirect
import sqlite3
import requests
import math
import os

import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)
database = 'datafile.db'


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(database)
    return g.sqlite_db


@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/")
def home():
    # 獲取資料
    cash_data = get_cash_data()
    stock_data, total_stock_value = get_stock_data()

    if cash_data['ud'] != 0 or cash_data['td'] != 0 or total_stock_value != 0:
        labels = ('TWD', 'USD', 'Stock')
        sizes = (cash_data['ud_to_td'], cash_data['td'], total_stock_value)
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sizes, labels=labels, autopct=None, shadow=None)
        fig.subplots_adjust(top=1, bottom=0, left=0,
                            right=1, hspace=0.5, wspace=0.5)
        plt.savefig("static/piechart2.jpg", dpi=200)
        plt.close(fig)
    else:
        try:
            os.remove("static/piechart2.jpg")
        except:
            pass

    # 判斷圖片是否存在
    pitcure_data = {'stock_picture': os.path.exists('static/piechart.jpg'),
                    'cash_picture': os.path.exists('static/piechart2.jpg')}
    return render_template("index.html", cash_data=cash_data, stock_data=stock_data, picture_data=pitcure_data)


@app.route("/cash_delete", methods=["POST"])
def cash_delete():
    transaction_id = request.values['id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """DELETE FROM cash WHERE transaction_id = ?""", (transaction_id,))

    conn.commit()
    return redirect("/")


@app.route("/cash")
def cash():
    return render_template("cash.html")


@app.route("/cash", methods=["POST"])
# 將提交的資料 存入資料庫
def submit_cash():
    taiwanese_dollars = 0
    us_dollars = 0
    if request.values['taiwanese-dollars']:
        taiwanese_dollars = request.values['taiwanese-dollars']
    if request.values['us-dollars']:
        us_dollars = request.values['us-dollars']
    note = request.values['note']
    date = request.values['date']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cash (taiwanese_dollars, us_dollars, note, date_info) VALUES (?, ?, ?, ?)",
                   (taiwanese_dollars, us_dollars, note, date))
    conn.commit()

    return redirect("/")


@app.route("/stock")
def stock():
    return render_template("stock.html")


@app.route("/stock", methods=["POST"])
# 將提交的資料 存入資料庫
def submit_stock():
    stock_id = request.values['stock-id']
    stock_num = request.values['stock-num']
    stock_price = request.values['stock-price']

    processing_fee = 0
    tax = 0
    if request.values['processing-fee']:
        processing_fee = request.values['processing-fee']
    if request.values['tax']:
        tax = request.values['tax']

    date = request.values['date']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stock (stock_id,stock_num, stock_price, processing_fee, tax, date_info) VALUES (?, ?, ?, ?, ?, ?)",
                   (stock_id, stock_num, stock_price, processing_fee, tax, date))
    conn.commit()

    return redirect("/")


def get_cash_data():
    # 獲得資料庫資料
    conn = get_db()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM cash")
    cash_data = result.fetchall()

    # 計算總金額
    total_taiwanese_dollars = 0
    total_US_dollars = 0
    for row in cash_data:
        total_taiwanese_dollars += row[1]
        total_US_dollars += row[2]

    # 得到實時匯率
    r = requests.get('https://tw.rter.info/capi.php')
    currency = r.json()
    total = math.floor(total_taiwanese_dollars +
                       total_US_dollars*currency['USDTWD']['Exrate'])
    ud_to_td = total_US_dollars*currency['USDTWD']['Exrate']

    # 傳送資料到前端
    data = {'total': total, 'currency': currency['USDTWD']['Exrate'],
            'ud': total_US_dollars, 'td': total_taiwanese_dollars, 'cash_data': cash_data, 'ud_to_td': ud_to_td}

    return data


def get_stock_data():
    # 獲得資料庫資料
    conn = get_db()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM stock")
    stock_data = result.fetchall()
    unique_stock_list = []

    for data in stock_data:
        if data[1] not in unique_stock_list:
            unique_stock_list.append(data[1])

    # 計算股票總市值
    total_stock_value = 0

    # 計算單一股票資訊
    stock_info = []

    for stock in unique_stock_list:
        result = cursor.execute(
            "select * from stock where stock_id = ?", (stock,))
        result = result.fetchall()

        # 計算總金額
        stock_cost = 0
        shares = 0

        for row in result:
            shares += row[2]
            stock_cost += row[2] * row[3] + row[4] + row[5]
            # 得到實時匯率
            url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo=" + stock
            r = requests.get(url)
            data = r.json()
            price_array = data["data"]
            currency_price = float(price_array[0][6].replace(',', ''))

            # 計算單一股票總市值
            total_value = int(currency_price * shares)
            total_stock_value += total_value
            # 單一股票平均成本
            average_cost = round(stock_cost/shares, 2)
            # 單一股票報酬率
            rate_of_return = round(
                (total_value - stock_cost) * 100 / stock_cost, 2)

            stock_info.append({
                'stock_id': stock,
                'stock_cost': stock_cost,
                'total_value': total_value,
                'average_cost': average_cost,
                'shares': shares,
                'currency_price': currency_price,
                'rate_of_return': rate_of_return,
            })
    for stock in stock_info:
        stock['value_percentage'] = round(
            stock['total_value']*100/total_stock_value, 2)

    if len(unique_stock_list) != 0:
        labels = tuple(unique_stock_list)
        sizes = [d['total_value'] for d in stock_info]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sizes, labels=labels, autopct=None, shadow=None)
        fig.subplots_adjust(top=1, bottom=0, left=0,
                            right=1, hspace=0.5, wspace=0.5)
        plt.savefig("static/piechart.jpg", dpi=200)
        plt.close(fig)
    else:
        try:
            os.remove("static/piechart2.jpg")
        except:
            pass

    return stock_info, total_stock_value


if __name__ == "__main__":
    app.run(debug=True)
