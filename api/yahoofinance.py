import api.base_api
import enums


# API Doc: https://www.yahoofinanceapi.com/
class YahooFinance(api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str, time_period: enums.TimePeriod = enums.TimePeriod.ONE_YEAR):
        params = {
            'symbol': symbol,
            'period': time_period.value,
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.YAHOOFINANCE, 'symbol/get-chart', params=params, use_secondary_url=True)
        return request.content