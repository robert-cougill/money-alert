import src.email.email_handler
import src.init
import src.report.base_report


class UnitTest:
    CONST_API_DOWN = '<img class="arrow-image-large" src="https://drive.google.com/uc?export=view&id={MONEY_ALERT_ARROW_DOWN}" />'.format(MONEY_ALERT_ARROW_DOWN=src.init.money_alert_arrow_down)
    CONST_API_UP = '<img class="arrow-image-large" src="https://drive.google.com/uc?export=view&id={MONEY_ALERT_ARROW_UP}" />'.format(MONEY_ALERT_ARROW_UP=src.init.money_alert_arrow_up)

    def __init__(self):
        src.init.logger.debug('Initialize Unit Test')
        self.email = src.email.email_handler.GMail()
        self.report = src.report.base_report.Report()

    def launch_unit_test(self):
        src.init.logger.debug('Enter item to scheduler')
        src.init.scheduler.enter(0, 1, self.__unit_test_health_check)

        src.init.logger.debug('Running scheduler')
        src.init.scheduler.run()

        src.init.logger.debug('Sending email')
        self.email.send_email('Money Alert - Unit Test')

    def __unit_test_health_check(self):
        headers = ['Bittrex', 'Coingecko']

        bittrex_ping_result = self.report.bittrex.ping()
        coingecko_ping_result = self.report.coingecko.get_ping()

        if bittrex_ping_result != 200 or coingecko_ping_result != 200:
            src.init.logger.warn(f'Bittrex API is returning the status code {bittrex_ping_result}')
            src.init.logger.warn(f'Coingecko API is returning the status code {coingecko_ping_result}')
            table = self.report.build_html_table(headers, {
                'bittrex': self.CONST_API_UP if bittrex_ping_result == 200 else self.CONST_API_DOWN,
                'coingecko': self.CONST_API_UP if coingecko_ping_result == 200 else self.CONST_API_DOWN
            }, 'unit_tests')
            self.email.add_report_to_email('Failed Health Check', table)
            return

        table = self.report.build_html_table(headers, {'bittrex': self.CONST_API_UP, 'coingecko': self.CONST_API_UP}, 'unit_tests')
        self.email.add_report_to_email('Successful Health Check', table)
