import src.api.base_api
import src.enums


# API Doc: https://rapidapi.com/alphavantage/api/alpha-vantage/
class AlphaVantage(src.api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str):
        params = {
            'symbol': symbol,
            'function': 'TIME_SERIES_DAILY',
            'outputsize': 'compact',
            'datatype': 'json'
        }

        request = src.api.base_api.BaseAPI.request_data(self, src.enums.APIClient.ALPHAVANTAGE, 'query', params=params)
        return request.content
