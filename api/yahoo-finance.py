import api.base_api
import enums


# API Doc: https://www.yahoofinanceapi.com/
class YahooFinance(api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str, time_frame: enums.YahooDataTimePeriod = enums.YahooDataTimePeriod.THREE_MONTH):
        params = {
            'symbol': symbol,
            'period': time_frame,
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.YAHOOFINANCE, 'symbol/get-chart', params=params, use_secondary_url=True)
        return request.content
