import ast
import bs4
import collections
import database_util
import email_handler
import init
import report.base_report
import requests
import socket
import urllib3
import util


class DinosaurFootprints(report.base_report.Report):
    def __init__(self):
        report.base_report.Report.__init__(self)
        self.wallets = []
        self.top_wallets = []
        self.insertion_wallet_addresses = []
        self.notify_nonexchange = dict()
        self.notify_exchange = dict()

    def run(self):
        self.__scrape_website('https://btc.com/stats/rich-list', 'table')
        self.__scrape_website('https://99bitcoins.com/bitcoin-rich-list-top500/', 't99btc-rich-list')
        self.__scrape_website('https://99bitcoins.com/bitcoin-rich-list-top1000/', 't99btc-rich-list')
        self.__add_new_wallet_addresses()
        self.__get_wallet_information()
        self.__attach_table_to_email()

    def pull_named_wallets(self):
        self.__bitinfocharts_pull_named_wallets()

    def __bitinfocharts_pull_named_wallets(self):
        bitinfo_urls = ['']
        for i in range(2, 101):
            bitinfo_urls.append('-' + str(i))

        exchange_wallet_addresses = collections.defaultdict(list)
        all_bitinfocharts_addresses = []
        bitinfocharts_wallet_links = []
        named_bitinfocharts_links = []
        db_wallet_addresses = []

        for url_ending in bitinfo_urls:
            response = requests.get('https://bitinfocharts.com/top-100-richest-bitcoin-addresses' + url_ending + '.html')
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            small_tags = soup.find_all('small')

            for tag in small_tags:
                for link in tag.find_all('a', href=True):
                    bitinfocharts_wallet_links.extend(['https://bitinfocharts.com' + link['href']])

        unique_links = list(set(bitinfocharts_wallet_links))

        for unique_link in unique_links:
            named_bitinfocharts_links += [unique_link]

        for named_link in named_bitinfocharts_links:
            try:
                response = requests.get(named_link, timeout=10)
                soup = bs4.BeautifulSoup(response.text, 'html.parser')
                addresses_container = soup.find_all('div', attrs={'id': 'ShowAddresesContainer'})

                for link in addresses_container:
                    for address_link in link.find_all('a', href=True):
                        exchange_wallet_addresses[named_link.split('/')[-1]] += [address_link.get_text()]
                        all_bitinfocharts_addresses.append(address_link.get_text())
            except (ValueError, urllib3.exceptions.InvalidChunkLength, urllib3.exceptions.ProtocolError, requests.exceptions.ChunkedEncodingError, urllib3.exceptions.ReadTimeoutError, socket.timeout, requests.exceptions.ConnectionError):
                init.logger.debug(f'Dinosaur Footprints - {named_link} failed to load properly.')

        con = database_util.DatabaseHelper().create_connection()
        rows = con.cursor().execute('SELECT DISTINCT wallet_address FROM top_bitcoin_wallet_report_data').fetchall()
        if len(rows) != 0:
            for row in rows:
                db_wallet_addresses.append(row[0])

        # Make sure we didn't miss any addresses already in the database
        for address in db_wallet_addresses:
            for exchange_name, exchange_wallet_address in exchange_wallet_addresses.items():
                if address in exchange_wallet_address and exchange_name.isnumeric():
                    self.insertion_wallet_addresses.append((address, 1, 'Unknown'))
                elif address in exchange_wallet_address and exchange_name.isnumeric() is False:
                    self.insertion_wallet_addresses.append((address, 1, exchange_name))

        # Insert all the Exchange wallet addresses as well
        for name, address in exchange_wallet_addresses.items():
            for value in address:
                if name.isnumeric():
                    self.insertion_wallet_addresses.append((value, 1, 'Unknown'))
                elif name.isnumeric() is False:
                    self.insertion_wallet_addresses.append((value, 1, name))

        con.cursor().executemany('INSERT INTO top_bitcoin_wallet_report_data (wallet_address, exchange_wallet, exchange_name) VALUES(?, ?, ?) ON CONFLICT (wallet_address) DO UPDATE SET (wallet_address, exchange_wallet, exchange_name) = (excluded.wallet_address, excluded.exchange_wallet, excluded.exchange_name)', self.insertion_wallet_addresses)
        con.commit()
        con.close()

    def __scrape_website(self, url, table_class_name):
        init.logger.debug(f'Dinosaur Footprints - Scraping {url}')
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table', attrs={'class': table_class_name})

        self.__extract_wallet_addresses(tables, self.wallets)

    @staticmethod
    def __extract_wallet_addresses(tables, wallets):
        init.logger.debug('Dinosaur Footprints - Extract Wallet Addresses')
        rows = []
        for table_index in range(len(tables)):
            rows.extend(tables[table_index].find_all('tr'))

        for row in rows:
            columns = row.find_all('td')
            values = []

            for field in columns:
                for link in field.find_all('a', href=True):
                    wallet_address = link['href'].split('/')[-1]
                    values.append(wallet_address)

            if values:
                wallets.append(values[0])

    def __add_new_wallet_addresses(self):
        init.logger.debug('Dinosaur Footprints - Adding new wallet addresses')
        con = database_util.DatabaseHelper().create_connection()
        rows = con.cursor().execute('SELECT DISTINCT wallet_address FROM top_bitcoin_wallet_report_data').fetchall()
        if len(rows) != 0:
            for row in rows:
                self.top_wallets.append(row[0])

        insert_list = []
        for wallet in self.wallets:
            if wallet not in self.top_wallets:
                insert_list.append(tuple([wallet]))
                init.logger.debug(f'Dinosaur Footprints - Inserting {wallet} into top_bitcoin_wallet_report_data')

        con.cursor().executemany('INSERT INTO top_bitcoin_wallet_report_data (wallet_address) VALUES(?) ON CONFLICT DO NOTHING', insert_list)
        con.commit()
        con.close()

    def __get_wallet_information(self):
        init.logger.debug('Dinosaur Footprints - Get Wallet Information')
        con = database_util.DatabaseHelper().create_connection()
        db_wallets = con.cursor().execute('SELECT * FROM top_bitcoin_wallet_report_data ORDER BY balance DESC').fetchall()

        db_wallet_dict = dict()
        for wallet in db_wallets:
            db_wallet_dict[wallet[0]] = {'balance': wallet[1], 'exchange_wallet': wallet[3]}

        # Pull wallet data from blockchain API
        blockchain_wallet_data = dict()
        wallet_list = []

        for wallet in db_wallet_dict:
            wallet_list.append(wallet)
            if len(wallet_list) % 50 == 0:
                wallet_data_in_bytes = self.blockchain.get_address_balances(wallet_list)
                wallet_data_decode = wallet_data_in_bytes.decode('UTF-8')
                blockchain_wallet_data.update(ast.literal_eval(wallet_data_decode))
                wallet_list = []

        if len(wallet_list) > 0:
            wallet_data_in_bytes = self.blockchain.get_address_balances(wallet_list)
            wallet_data_decode = wallet_data_in_bytes.decode('UTF-8')
            blockchain_wallet_data.update(ast.literal_eval(wallet_data_decode))

        for wallet_address, wallet_data in blockchain_wallet_data.items():
            # If DB is missing balance or total_received, add to DB and continue
            if db_wallet_dict[wallet_address]['balance'] is not None:
                self.__compare_wallet_information(db_wallet_dict[wallet_address], wallet_data, wallet_address)

            update_statement = 'UPDATE top_bitcoin_wallet_report_data SET balance = ? WHERE wallet_address = ?'
            con.cursor().execute(update_statement, tuple([wallet_data['final_balance'], wallet_address]))

        con.commit()
        if len(self.notify_nonexchange) > 0:
            self.notify_nonexchange = self.__sort_dictionary(self.notify_nonexchange)

        if len(self.notify_exchange) > 0:
            self.notify_exchange = self.__sort_dictionary(self.notify_exchange)

    @staticmethod
    def __sort_dictionary(dictionary):
        return dict(sorted(dictionary.items(), key=lambda item: item[1]))

    def __compare_wallet_information(self, db_wallet, blockchain_wallet, wallet_address):
        if db_wallet['balance'] != blockchain_wallet['final_balance']:
            balance_diff = util.convert_satoshis_to_btc(blockchain_wallet['final_balance'] - db_wallet['balance'])

            if balance_diff > init.config['report_settings']['dinosaur_footprints_btc_transaction_threshold'] or balance_diff < -init.config['report_settings']['dinosaur_footprints_btc_transaction_threshold']:
                if db_wallet['exchange_wallet'] == 0:
                    self.notify_nonexchange[wallet_address] = balance_diff
                if db_wallet['exchange_wallet'] == 1:
                    self.notify_exchange[wallet_address] = balance_diff

    def __attach_table_to_email(self):
        init.logger.info(f'Dinosaur Footprints - Non-Exchange Wallets Found: {len(self.notify_nonexchange)}')
        init.logger.info(f'Dinosaur Footprints - Exchange Wallets Found: {len(self.notify_exchange)}')
        email = email_handler.GMail()

        if len(self.notify_nonexchange) == 0:
            email.add_report_to_email('Dinosaur Footprints - Non-Exchange Report', self.build_no_data_result())
        else:
            nonexchange_table = self.build_html_table(['Wallet', 'Balance Change'], self.notify_nonexchange, 'dinosaur_footprints')
            email.add_report_to_email('Dinosaur Footprints - Non-Exchange Report', nonexchange_table)

        if len(self.notify_exchange) == 0:
            email.add_report_to_email('Dinosaur Footprints - Exchange Report', self.build_no_data_result())
        else:
            exchange_table = self.build_html_table(['Wallet', 'Balance Change'], self.notify_exchange, 'dinosaur_footprints')
            email.add_report_to_email('Dinosaur Footprints - Exchange Report', exchange_table)
