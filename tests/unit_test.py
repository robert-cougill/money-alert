import email_handler
import init
import report.base_report


class UnitTest:
    CONST_API_DOWN = '<img class="arrow-image-large" src="https://drive.google.com/uc?export=view&id=MONEY_ALERT_ARROW_DOWN" />'
    CONST_API_UP = '<img class="arrow-image-large" src="https://drive.google.com/uc?export=view&id=MONEY_ALERT_ARROW_UP" />'

    def __init__(self):
        init.logger.debug('Initialize Unit Test')
        self.gmail = email_handler.GMail()
        self.report = report.base_report.Report()

    def launch_unit_test(self):
        init.logger.debug('Enter item to scheduler')
        init.scheduler.enter(0, 1, self.__unit_test_health_check)

        init.logger.debug('Running scheduler')
        init.scheduler.run()

        init.logger.debug('Sending email')
        self.gmail.build_and_send_gmail(init.config['emails'], 'Money Alert - Unit Test')

    def __unit_test_health_check(self):
        headers = ['Bittrex', 'Coingecko']

        bittrex_ping_result = self.report.bittrex.ping()
        coingecko_ping_result = self.report.coingecko.get_ping()

        if bittrex_ping_result != 200 or coingecko_ping_result != 200:
            init.logger.warn(f'Bittrex API is returning the status code {bittrex_ping_result}')
            init.logger.warn(f'Coingecko API is returning the status code {coingecko_ping_result}')
            table = self.report.build_html_table(headers, {
                'bittrex': self.CONST_API_UP if bittrex_ping_result == 200 else self.CONST_API_DOWN,
                'coingecko': self.CONST_API_UP if coingecko_ping_result == 200 else self.CONST_API_DOWN
            }, 'unit_tests')
            self.gmail.add_email_content('Failed Health Check', table)
            return

        table = self.report.build_html_table(headers, {'bittrex': self.CONST_API_UP, 'coingecko': self.CONST_API_UP}, 'unit_tests')
        self.gmail.add_email_content('Successful Health Check', table)
