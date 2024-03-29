import src.report.chart_builder
import src.utils.database_util
import datetime
import src.email.email_handler
import src.init
import json
import src.report.base_report
import src.utils.util
import traceback


class MovingAverages(src.report.base_report.Report):
    CONST_REPORT = 'moving_average'
    CONST_REPORT_TITLE = 'Moving Average'
    CONST_CHART_FILE_DIRECTORY = src.utils.util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.charts = src.report.chart_builder.ChartBuilder()
        self.coin_history = dict()

    def build_report_data(self):
        src.init.logger.info(f'Moving Average - Starting to Build {self.CONST_REPORT_TITLE} Report Data')
        self.__build_historical_coin_data()
        src.init.logger.info(f'Moving Average - Finished Building {self.CONST_REPORT_TITLE} Report Data')

    def run(self):
        email = src.email.email_handler.GMail()

        try:
            self.__validate_report_data()

            self.charts.build_charts_for_report(self.coin_history)

            coins = dict()
            for coin, price in self.coin_history.items():
                coins[coin] = price[0]

            sorted_coins = dict(sorted(coins.items(), key=lambda item: item[1], reverse=True))
            ordered_coins = sorted_coins.keys()

            image_body = self.embed_images(src.utils.util.list_chart_files(self.CONST_CHART_FILE_DIRECTORY), ordered_coins)
            email.add_report_to_email('Moving Averages', image_body)
            email.send_email('Moving Averages')

            src.utils.util.remove_charts_from_directory(self.CONST_CHART_FILE_DIRECTORY)
            src.init.logger.info('Moving Averages Report Completed')

        except Exception as e:
            email.add_report_to_email('Moving Average', str(e) + '<br/><br/>' + traceback.format_exc())
            return

    def __validate_report_data(self):
        self.__read_data_from_db()
        self.__build_historical_coin_data()

        today_time = datetime.datetime.now()
        today_date = today_time.strftime('%m-%d-%Y')

        con = src.utils.database_util.DatabaseHelper().create_connection()
        last_run = con.cursor().execute('SELECT last_run_datetime FROM report_run_time WHERE report_name = ?', tuple([self.CONST_REPORT])).fetchone()
        con.close()

        if last_run is None or last_run[0] != today_date:
            self.__get_current_price_and_adjust_history()
            src.utils.database_util.DatabaseHelper().update_report_run_time(self.CONST_REPORT, today_date)

    def __build_historical_coin_data(self):
        for coin in src.init.coin_list.values():
            if not (coin in self.coin_history):
                src.init.logger.warning(f'Moving Average - Building data list for {coin}. This will take a few minutes.')
                time_now = datetime.datetime.now()
                data_list = []

                for day in range(1, 366):
                    date = time_now - datetime.timedelta(days=day)
                    formatted_date = date.strftime('%d-%m-%Y')
                    response = json.loads(self.coingecko.get_coin_history(coin, formatted_date))

                    try:
                        data_list.append(response['market_data']['current_price']['usd'])
                    except KeyError:
                        src.init.logger.info(f"Moving Average - No market_data for coin {coin} on date {date.strftime('%Y-%m-%d')}")

                src.init.logger.warning(f'Moving Average - Finished building list for {coin}')
                self.coin_history[coin] = data_list

        self.__write_data_to_db()

    def __get_current_price_and_adjust_history(self):
        src.init.logger.debug('Moving Average - Adjusting History')
        for coin in src.init.coin_list.values():
            date_now = datetime.datetime.now() - datetime.timedelta(days=1)
            formatted_date = date_now.strftime('%d-%m-%Y')
            response = json.loads(self.coingecko.get_coin_history(coin, formatted_date))
            self.coin_history[coin].insert(0, response['market_data']['current_price']['usd'])

            # Remove last list element
            self.coin_history[coin].pop()

        self.__write_data_to_db()

    def __write_data_to_db(self):
        src.init.logger.debug('Moving Average - Write Data to DB')
        con = src.utils.database_util.DatabaseHelper().create_connection()

        insert_list = []
        for key, value in self.coin_history.items():
            insert_tuple = (key, str('|'.join([str(i) for i in value])))
            insert_list.append(insert_tuple)

        con.cursor().executemany('INSERT INTO moving_average_report_data(coin_id, date_specific_data) VALUES(?,?) ON CONFLICT (coin_id) DO UPDATE SET (date_specific_data) = (excluded.date_specific_data)', insert_list)
        con.commit()
        con.close()

    def __read_data_from_db(self):
        src.init.logger.debug('Moving Average - Read Data From DB')
        con = src.utils.database_util.DatabaseHelper().create_connection()

        select_statement = 'SELECT coin_id, date_specific_data FROM moving_average_report_data'
        rows = con.cursor().execute(select_statement).fetchall()
        con.close()

        for row in rows:
            string_list = row[1].split('|')
            self.coin_history[row[0]] = [float(x) for x in string_list]
