import sqlite3
import util


class DatabaseHelper:
    CONST_DB_LOCATION = util.configure_file_path('report/report_data/money_alert_database.db')

    def create_connection(self):
        """
        create a database connection to the SQLite database specified by db_file
        :return: Connection object or None
        """
        con = None
        try:
            con = sqlite3.connect(self.CONST_DB_LOCATION)
        except sqlite3.Error as e:
            print(e)

        return con

    def create_database(self):
        con = self.create_connection()
        cur = con.cursor()

        # Daily Report Run - to track the last run time for the daily report
        cur.execute('CREATE TABLE IF NOT EXISTS report_run_time (report_name TEXT PRIMARY KEY, last_run_datetime INTEGER NULL)')

        # Trending report
        cur.execute('CREATE TABLE IF NOT EXISTS trending_report_data (coingecko_id TEXT PRIMARY KEY, appearances INTEGER NOT NULL, modify_date INTEGER)')

        # Top BTC wallets - All values are in satoshis (super asian)
        cur.execute('CREATE TABLE IF NOT EXISTS top_bitcoin_wallet_report_data (wallet_address TEXT PRIMARY KEY, balance INTEGER NULL, total_received INTEGER NULL, exchange_wallet NUMERIC DEFAULT 0 NOT NULL, exchange_name TEXT)')

        # Moving averages
        # get_coin_history date must be in the DD-MM-YYYY format
        cur.execute('CREATE TABLE IF NOT EXISTS moving_average_report_data (coin_id TEXT PRIMARY KEY, date_specific_data TEXT)')

        # Public Company Holdings
        cur.execute('CREATE TABLE IF NOT EXISTS public_company_holdings (company_name TEXT, coin text, total_holdings NUMERIC)')

        con.commit()
        con.close()

    def update_report_run_time(self, report_name: str, last_run: str):
        con = self.create_connection()
        con.cursor().execute('INSERT INTO report_run_time(report_name, last_run_datetime) VALUES (?,?) ON CONFLICT(report_name) DO UPDATE SET (last_run_datetime) = (excluded.last_run_datetime)', tuple([report_name, last_run]))
        con.commit()
        con.close()
