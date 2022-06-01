from src import init, email_handler
import json
import src.report.base_report
import time


class DipWatcher(src.report.base_report.Report):
    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.price_dict = dict()
        self.price_dict['bitcoin'] = list()
        self.last_email_sent = time.time()

    def run(self):
        one_hour_percent_change = 0
        two_hour_percent_change = 0
        four_hour_percent_change = 0
        eight_hour_percent_change = 0
        twelve_hour_percent_change = 0

        current_price = self.blockchain.get_current_price('BTC-USD')
        if current_price is None:
            init.logger.info('Dip Watcher - API returned a null value')
            return

        response = json.loads(current_price)
        if 'last_trade_price' not in response:
            init.logger.info(f'Dip Watcher - Response is missing key: {response}')
            return

        self.price_dict['bitcoin'].insert(0, response['last_trade_price'])

        if len(self.price_dict['bitcoin']) >= 60:
            one_hour_percent_change = (self.price_dict['bitcoin'][0] - self.price_dict['bitcoin'][59]) / self.price_dict['bitcoin'][59] * 100

        if len(self.price_dict['bitcoin']) >= 120:
            two_hour_percent_change = (self.price_dict['bitcoin'][0] - self.price_dict['bitcoin'][119]) / self.price_dict['bitcoin'][119] * 100

        if len(self.price_dict['bitcoin']) >= 240:
            four_hour_percent_change = (self.price_dict['bitcoin'][0] - self.price_dict['bitcoin'][239]) / self.price_dict['bitcoin'][239] * 100

        if len(self.price_dict['bitcoin']) >= 480:
            eight_hour_percent_change = (self.price_dict['bitcoin'][0] - self.price_dict['bitcoin'][479]) / self.price_dict['bitcoin'][479] * 100

        if len(self.price_dict['bitcoin']) == 720:
            twelve_hour_percent_change = (self.price_dict['bitcoin'][0] - self.price_dict['bitcoin'][719]) / self.price_dict['bitcoin'][719] * 100
            self.price_dict['bitcoin'].pop()

        init.logger.info(f'Price: {self.price_dict["bitcoin"][0]} | 1: {one_hour_percent_change} | 2: {two_hour_percent_change} | 4: {four_hour_percent_change} | 8: {eight_hour_percent_change} | 12: {twelve_hour_percent_change}')

        watcher_threshold = init.config['report_settings']['watcher_threshold']
        if (one_hour_percent_change <= watcher_threshold
                or two_hour_percent_change <= watcher_threshold
                or four_hour_percent_change <= watcher_threshold
                or eight_hour_percent_change <= watcher_threshold
                or twelve_hour_percent_change <= watcher_threshold):

            # only send once for the amount of time in seconds
            if (time.time() - self.last_email_sent) > 600:
                self.last_email_sent = time.time()
                email = email_handler.GMail()
                email.send_email('BTC has dipped! Current Price: ' + '{:.2f}'.format(self.price_dict['bitcoin'][0]))
