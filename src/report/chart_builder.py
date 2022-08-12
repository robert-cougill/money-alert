import matplotlib.pyplot as plt
import matplotlib.offsetbox as box
import numpy
import src.utils.util


class ChartBuilder:
    CONST_CHART_FILE_DIRECTORY = src.utils.util.configure_file_path('report/report_data/charts/')

    def build_charts_for_report(self, asset_history, use_title_case: bool = True):
        for asset, historical_data in asset_history.items():
            self.build_single_chart(asset, historical_data, use_title_case)

    def build_single_chart(self, asset_name: str, historic_data: list, use_title_case: bool = True):
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

        if use_title_case:
            ax.set(title=asset_name.replace('-', ' ').title(), xlabel='Days', ylabel='Price (USD)')
        else:
            ax.set(title=asset_name, xlabel='Days', ylabel='Price (USD)')


        # Plot list, min, and max values
        ax.plot(x, historic_data, linestyle='-', color='#127700')
        ax.plot(max_x, max_y, marker='o', color='#33d23d')
        ax.plot(min_x, min_y, marker='o', color='#dc3131')

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

        ax.add_artist(
            box.AnchoredText(
                str(round(historic_data[0], 2)),
                loc='lower right', prop=dict(size=10), frameon=False,
                bbox_to_anchor=(1.01, .985),
                bbox_transform=ax.transAxes))

        plt.savefig(self.CONST_CHART_FILE_DIRECTORY + asset_name + '.png')
        plt.close(fig)
