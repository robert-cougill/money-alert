import api.bittrex
import api.blockchain
import api.coingecko
import api.yahoofinance
import init
import json
import typing


class Report:
    def __init__(self):
        self.bittrex = api.bittrex.Bittrex()
        self.blockchain = api.blockchain.Blockchain()
        self.coingecko = api.coingecko.Coingecko()
        self.yahoofinance = api.yahoofinance.YahooFinance()

    def get_current_price_of_all_coins(self) -> typing.Dict:
        current_coin_price = dict()
        coin_price = self.coingecko.get_simple_price(init.coin_list)
        coins = json.loads(coin_price)

        for i in coins:
            current_coin_price[i] = coins[i]['usd']

        return current_coin_price

    def embed_images(self, file_names, ordered_coins) -> str:
        body = '<body>'

        for coins in ordered_coins:
            for file_name in file_names:
                if coins == file_name.split('.')[0]:
                    body += '<img class="charts" src="cid:' + file_name.split('.')[0] + '" alt="' + file_name + '">'
                    continue

        body += '</body>'
        return body

    def build_html_table(self, headers: typing.List, body: typing.Dict, report_name=None) -> str:
        table = '<table class="styled-table"><thead><tr>'
        for header in headers:
            table += '<th>' + header + '</th>'

        table += '</tr></thead>'

        if report_name == 'unit_tests':
            for key, value in body.items():
                table += '<td>' + str(value) + '</td>'
        elif report_name == 'trending':
            for key, value in body.items():
                coin_name = key.replace('-', ' ').title()
                table += '<tr><td><a href="https://www.coingecko.com/en/coins/' + str(key) + '">' + coin_name + '</a></td>' + str(value) + '</td></tr>'
        elif report_name == 'public_company_holdings':
            for key, value in body.items():
                table += '<tr><td>' + str(value['company']) + '</td><td>' + str(value['coin']) + '</td>'
                table += '<td>' + str(value['change']) + '</td><td>' + str(value['total_holdings']) + '</td></tr>'
        elif report_name == 'dinosaur_footprints':
            for key, value in body.items():
                table += '<tr><td><a href="https://www.blockchain.com/btc/address/' + str(key) + '">' + key[:5] + '...' + key[-5:] + '</a></td>'
                if value > 0:
                    table += '<td class="positive">' + str(value) + '</td></tr>'
                else:
                    table += '<td class="negative">' + str(value) + '</td></tr>'

        table += '</table>'
        return table
