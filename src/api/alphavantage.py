import api.base_api
import enums


# API Doc: https://rapidapi.com/alphavantage/api/alpha-vantage/
class AlphaVantage(api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str):
        params = {
            'symbol': symbol,
            'function': 'TIME_SERIES_DAILY',
            'outputsize': 'compact',
            'datatype': 'json'
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.ALPHAVANTAGE, 'query', params=params)
        return request.content
