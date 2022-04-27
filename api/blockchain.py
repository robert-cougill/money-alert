import api.base_api
import enums


# API Doc: https://www.blockchain.com/api/blockchain_api
# API Doc: https://api.blockchain.com/v3/
class Blockchain(api.base_api.BaseAPI):
    def get_current_price(self, symbol: str):
        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BLOCKCHAIN_V3, 'tickers', endpoint_args=symbol)
        if request is None:
            return None

        return request.content

    def get_address_balances(self, wallet_addresses: list):
        address_list = '|'.join(wallet_addresses)
        params = {
            'active': address_list
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BLOCKCHAIN, 'balance', params=params)
        return request.content

    def get_multi_address(self, wallet_addresses: list):
        address_list = '|'.join(wallet_addresses)
        params = {
            'active': address_list
        }

        request = api.base_api.BaseAPI.request_data(self, enums.APIClient.BLOCKCHAIN, 'multiaddr', params=params)
        return request.content
