import api.base_api
from datetime import datetime, timedelta
import enums


# API Doc: https://metalpriceapi.com/documentation
import init


class MetalPrice(api.base_api.BaseAPI):
    def get_historical_data(self, symbol: str):
        end_date = datetime.now()
        start_date = end_date.today() - timedelta(days=364)
        params = {
            'base': 'USD',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'currencies': symbol
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.METALPRICE, 'timeframe', params=params)
        return request.content
