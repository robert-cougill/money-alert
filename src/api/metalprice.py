import src.api.base_api
import datetime
import src.enums


# API Doc: https://metalpriceapi.com/documentation
class MetalPrice(src.api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str):
        end_date = datetime.datetime.now()
        start_date = end_date.today() - datetime.timedelta(days=364)
        params = {
            'base': 'USD',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'currencies': symbol
        }

        request = src.api.base_api.BaseAPI.request_data(self, src.enums.APIClient.METALPRICE, 'timeframe', params=params)
        return request.content
