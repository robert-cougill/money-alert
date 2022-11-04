import src.email.email_handler
import src.report.chart_builder
import src.init
import json
import src.report.base_report
import src.utils.util
import traceback


class StockTracker(src.report.base_report.Report):
    CONST_CHART_FILE_DIRECTORY = src.utils.util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.charts = src.report.chart_builder.ChartBuilder()
        self.stock_history = dict()

    def run(self):
        email = src.email.email_handler.GMail()

        try:
            src.init.logger.info(f'Stock Tracker - Stock Symbols: {src.init.config["stock_symbols"]}')
            for symbol in src.init.config['stock_symbols']:
                historical_data = json.loads(self.alphavantage.get_historical_data(symbol))
                if 'Time Series (Daily)' not in historical_data:
                    return

                closing_values = []
                history = historical_data['Time Series (Daily)']
                for key in history.keys():
                    closing_values.append(float(history[key]['4. close']))

                self.stock_history[symbol] = closing_values

            self.charts.build_charts_for_report(self.stock_history, False)
            image_body = self.embed_images(src.utils.util.list_chart_files(self.CONST_CHART_FILE_DIRECTORY), src.init.config['stock_symbols'])
            email.add_report_to_email('Stock Tracker', image_body)
            src.init.logger.info(f'Stock Tracker - Stock Symbols: {src.init.config["stock_symbols"]}')

        except Exception as e:
            email.add_report_to_email('Stock Tracker', str(e) + '<br/><br/>' + traceback.format_exc())
            return

    def cleanup_charts(self):
        src.utils.util.remove_charts_from_directory(self.CONST_CHART_FILE_DIRECTORY)
