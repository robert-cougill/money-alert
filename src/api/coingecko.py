import src.api.base_api
from src import enums
import typing


# API Doc: https://www.coingecko.com/api/documentations/v3/
class Coingecko(src.api.base_api.BaseAPI):
    def get_ping(self):
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'ping')
        return request.status_code

    def get_simple_price(self, coin_list: typing.Dict):
        concat_coins = ''
        first_loop = True
        for i in coin_list:
            if first_loop:
                concat_coins += coin_list[i]
                first_loop = False
                continue

            concat_coins += ',' + coin_list[i]

        args = 'price'
        params = {
            'ids': concat_coins,
            'vs_currencies': 'usd',
        }

        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'simple', endpoint_args=args, params=params)
        return request.content

    def get_simple_supported_vs_currency(self):
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'simple/supported_vs_currencies')
        return request.content

    def get_coins_list(self, include_platform: bool = False):
        params = {
            'include_platform': include_platform
        }
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins/list', params=params)
        return request.content

    def get_coins_by_id(self, coin_id: str):
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins', endpoint_args=coin_id)
        return request.content

    def get_coin_history(self, coin_id: str, historical_date: str):
        """ Date must be in the DD-MM-YYYY format """
        args = coin_id + '/history'
        params = {
            'date': historical_date
        }

        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins', endpoint_args=args, params=params)
        return request.content

    def get_market_chart(self, coin_id: str, days_ago: int, data_interval: enums.DataInterval = enums.DataInterval.DAILY):
        args = coin_id + '/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days_ago,
            'interval': data_interval.value
        }

        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins', endpoint_args=args, params=params)
        return request.content

    def get_market_chart_range(self, coin_id: str, from_date: int, to_date: int):
        """ Date must be in the Unix Timestamp format """
        args = coin_id + '/market_chart/range'
        params = {
            'vs_currency': 'usd',
            'from': from_date,
            'to': to_date
        }

        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins', endpoint_args=args, params=params)
        return request.content

    def get_markets(self, price_change_percentage: str):
        """ Include price change percentage in 1h, 24h, 7d, 14d, 30d, 200d, 1y (e.g. '1h,24h,7d' comma-separated, invalid values will be discarded) """
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum',
            'price_change_percentage': price_change_percentage
        }

        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'coins/markets', params=params)
        return request.content

    def get_trending(self):
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'search/trending')
        return request.content

    def get_public_company_holdings(self, coin_id: str):
        request = src.api.base_api.BaseAPI.request_data(self, enums.APIClient.COINGECKO, 'companies/public_treasury', endpoint_args=coin_id)
        return request.content
