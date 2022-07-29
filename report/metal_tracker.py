import email_handler
import chart_builder
import init
import json
import report.base_report
import util


class MetalTracker(report.base_report.Report):
    CONST_CHART_FILE_DIRECTORY = util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        report.base_report.Report.__init__(self)
        self.charts = chart_builder.ChartBuilder()
        self.metal_history = dict()
        self.metal_names = {'XAU': 'Gold', 'XAG': 'Silver'}

    def run(self):
        for symbol in init.config['metal_symbols']:
            historical_data = json.loads(self.metalprice.get_historical_data(symbol))
            if 'rates' not in historical_data:
                return

            rates = []
            history = historical_data['rates']
            for date, metal in history.items():
                if symbol in metal:
                    rates.append(1/metal[symbol])

            name = self.metal_names[symbol]
            self.metal_history[name] = rates

        self.charts.build_charts_for_report(self.metal_history, False)
        image_body = self.embed_images(util.list_chart_files(self.CONST_CHART_FILE_DIRECTORY), self.metal_names.values())
        email = email_handler.GMail()
        email.add_report_to_email('Metal Tracker', image_body)

    def cleanup_charts(self):
        util.remove_charts_from_directory(self.CONST_CHART_FILE_DIRECTORY)
