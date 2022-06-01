import email_handler
import chart_builder
import init
import json
import report.base_report
import util


class StockTracker(report.base_report.Report):
    CONST_CHART_FILE_DIRECTORY = util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        report.base_report.Report.__init__(self)
        self.charts = chart_builder.ChartBuilder()
        self.stock_history = dict()

    def run(self):
        init.logger.info(f'Stock Tracker - Stock Symbols: {init.config["stock_symbols"]}')
        for symbol in init.config['stock_symbols']:
            historical_data = json.loads(self.yahoofinance.get_historical_data(symbol))
            closing_values = []

            if 'attributes' not in historical_data:
                return

            history = historical_data['attributes']
            for key in sorted(history.keys()):
                closing_values.append(history[key]['close'])

            closing_values.reverse()
            self.stock_history[symbol] = closing_values

        self.charts.build_charts_for_report(self.stock_history, False)
        image_body = self.embed_images(util.list_chart_files(self.CONST_CHART_FILE_DIRECTORY), init.config['stock_symbols'])
        email = email_handler.GMail()
        email.add_report_to_email('Stock Tracker', image_body)

    def cleanup_charts(self):
        util.remove_charts_from_directory(self.CONST_CHART_FILE_DIRECTORY)
