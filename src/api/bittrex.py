import api.base_api
import enums


class Bittrex(api.base_api.BaseAPI):
    def ping(self):
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BITTREX, 'ping')
        return request.status_code

    # API Doc: https://bittrex.github.io/api/v3#operation--currencies--symbol--get
    def get_currency(self, symbol: str):
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BITTREX, 'currencies', endpoint_args=symbol)
        return request.content

    # API Doc: https://bittrex.github.io/api/v3#operation--markets-summaries-get
    def overall_market_summary(self):
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BITTREX, 'markets/summaries')
        return request.content

    # API Doc: https://bittrex.github.io/api/v3#operation--markets--marketSymbol--summary-get
    def coin_market_summary(self, symbol: str):
        args = symbol + '/summary'
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BITTREX, 'markets', endpoint_args=args)
        return request.content

    # API Doc: https://bittrex.github.io/api/v3#operation--markets--marketSymbol--ticker-get
    def coin_market_ticker(self, symbol: str):
        args = symbol + '/ticker'
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BITTREX, 'markets', endpoint_args=args)
        return request.content
