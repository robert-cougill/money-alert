import logging
import matplotlib.pyplot as plt
import matplotlib.offsetbox as box
import numpy
import os
import util


class ChartBuilder:
    CONST_CHART_FILE_DIRECTORY = util.configure_file_path('report/report_data/charts/')

    def __init__(self):
        logging.getLogger().setLevel(level=logging.INFO)

    def build_charts_for_moving_averages(self, coin_history):
        for coin, history in coin_history.items():
            self.build_single_chart(coin, history)

    def build_single_chart(self, coin_name: str, historic_data):
        if len(historic_data) == 0:
            return

        x = [*range(1, len(historic_data) + 1)]

        max_y = numpy.amax(historic_data)
        max_x = historic_data.index(max_y) + 1

        min_y = numpy.amin(historic_data)
        min_x = historic_data.index(min_y) + 1

        # Set up chart plot
        plt.set_loglevel('info')
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(len(x), 0)
        ax.set(title=coin_name.replace('-', ' ').title(), xlabel='Days', ylabel='Price (USD)')

        # Plot list, min, and max values
        ax.plot(x, historic_data, linestyle='-', color='#179de2')
        ax.plot(max_x, max_y, marker='o', color='#24a916')
        ax.plot(min_x, min_y, marker='o', color='#e21717')

        # Display numeric values for min and max
        ax.add_artist(
            box.AnnotationBbox(
                box.TextArea(str(round(min_y, 2))),
                (min_x, min_y),
                xybox=(1.02, min_y),
                boxcoords=('axes fraction', 'data'),
                box_alignment=(0., 0.5),
                arrowprops=dict(arrowstyle='-', color='gray')))

        ax.add_artist(
            box.AnnotationBbox(
                box.TextArea(str(round(max_y, 2))),
                (max_x, max_y),
                xybox=(1.02, max_y),
                boxcoords=('axes fraction', 'data'),
                box_alignment=(0., 0.5),
                arrowprops=dict(arrowstyle='-', color='gray')))

        plt.savefig(self.CONST_CHART_FILE_DIRECTORY + coin_name + '.png')

    def list_chart_files(self):
        return os.listdir(self.CONST_CHART_FILE_DIRECTORY)

    def remove_charts_from_directory(self):
        files = self.list_chart_files()
        for file in files:
            os.remove(self.CONST_CHART_FILE_DIRECTORY + file)
