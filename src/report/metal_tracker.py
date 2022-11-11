import src.email.email_handler
import src.report.chart_builder
import src.init
import json
import src.report.base_report
import src.utils.util
import traceback


class MetalTracker(src.report.base_report.Report):
    CONST_CHART_FILE_DIRECTORY = src.utils.util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.charts = src.report.chart_builder.ChartBuilder()
        self.metal_history = dict()
        self.metal_names = {'XAU': 'Gold', 'XAG': 'Silver'}

    def run(self):
        email = src.email.email_handler.GMail()

        try:
            for symbol in src.init.config['metal_symbols']:
                historical_data = json.loads(self.metalprice.get_historical_data(symbol))
                if 'rates' not in historical_data:
                    return

                rates = []
                history = historical_data['rates']
                for date, metal in history.items():
                    if symbol in metal:
                        rates.append(1/metal[symbol])

                name = self.metal_names[symbol]
                rates.reverse()
                self.metal_history[name] = rates

            self.charts.build_charts_for_report(self.metal_history, False)
            image_body = self.embed_images(src.utils.util.list_chart_files(self.CONST_CHART_FILE_DIRECTORY), self.metal_names.values())
            email.add_report_to_email('Metal Tracker', image_body)
            src.init.logger.info('Metal Tracker Completed')

        except Exception as e:
            email.add_report_to_email('Metal Tracker', str(e) + '<br/><br/>' + traceback.format_exc())
            return
