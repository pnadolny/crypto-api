from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from prettytable import PrettyTable
from decimal import Decimal
import json


f = open("data.json","r")
data = json.load(f)
f.close()

url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

parameters = {"symbol": ",".join(data.keys())}


f = open("config.json","r")
config_data = json.load(f)
f.close()

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": config_data.get("api_key"),
}

# Color
R = "\033[0;31;40m"  # RED
G = "\033[0;32;40m"  # GREEN
Y = "\033[0;33;40m"  # Yellow
B = "\033[0;34;40m"  # Blue
N = "\033[0m"  # Reset


def colorMe(value):
    if value > 0:
        colored_value = G + str(round(value, 2)) + N
    else:
        colored_value = R + str(round(value, 2)) + N
    return colored_value


session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    response_data = json.loads(response.text)
    print()
    print("Timestamp:" + response_data.get("status").get("timestamp"))
    pt = PrettyTable()
    pt.field_names = [
        "Coin",
        "Name",
        "Price",
        "1h",
        "24h",
        "7d",
        "30d",
        "Vol24h",
        "Cost",
        "Balance",
        "G/L",
        "%",
    ]
    total_cost, total_balance = 0, 0
    formatCurrency = lambda s: "${:,.2f}".format(s)
    for _, (symbol, coin) in enumerate(response_data.get("data").items()):
        quote = coin.get("quote").get("USD")
        balance = Decimal(quote.get("price")) * Decimal(
            data[symbol.lower()].get("satoshi")
        )
        total_balance += balance
        cost = Decimal(data[symbol.lower()].get("cost"))
        total_cost += cost
        gain_loss = round(balance - cost, 2)
        gain_loss_no_fees = 0
        perc = ((balance - cost) / cost) * 100
        pt.add_row(
            [
                B + symbol + N,
                coin.get("name"),
                formatCurrency(round(quote.get("price"), 2)),
                colorMe(quote["percent_change_1h"]),
                colorMe(quote["percent_change_24h"]),
                colorMe(quote["percent_change_7d"]),
                colorMe(quote["percent_change_30d"]),
                colorMe(quote["volume_change_24h"]),
                formatCurrency(round(cost, 2)),
                formatCurrency(round(balance, 2)),
                colorMe(gain_loss),
                colorMe(perc),
            ]
        )
    pt.align = "r"

    totalTable = PrettyTable()
    totalTable.field_names = ["Balance", "Cost", "G/L", "%"]
    gain_loss_percentage = round((total_balance - total_cost) / total_cost, 3)
    totalTable.align = "r"
    totalTable.add_row(
        [
            formatCurrency(round(total_balance, 2)),
            formatCurrency(round(total_cost, 2)),
            colorMe(total_balance - total_cost),
            colorMe(gain_loss_percentage),
        ]
    )
    print(totalTable)

    print(pt.get_string(sortby="G/L"))


except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
