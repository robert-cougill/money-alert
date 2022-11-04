import src.api.base_api
import src.enums


# API Doc: https://www.blockchain.com/api/blockchain_api
# API Doc: https://api.blockchain.com/v3/
class Blockchain(src.api.base_api.BaseAPI):
    def get_current_price(self, symbol: str, continue_on_error: bool = False):
        request = src.api.base_api.BaseAPI.request_data(self, src.enums.APIClient.BLOCKCHAIN_V3, 'tickers', endpoint_args=symbol, continue_on_error=continue_on_error)
        if request is None:
            return None

        return request.content

    def get_address_balances(self, wallet_addresses: list):
        address_list = '|'.join(wallet_addresses)
        params = {
            'active': address_list
        }

        request = src.api.base_api.BaseAPI.request_data(self, src.enums.APIClient.BLOCKCHAIN, 'balance', params=params)
        return request.content

    def get_multi_address(self, wallet_addresses: list):
        address_list = '|'.join(wallet_addresses)
        params = {
            'active': address_list
        }

        request = src.api.base_api.BaseAPI.request_data(self, src.enums.APIClient.BLOCKCHAIN, 'multiaddr', params=params)
        return request.content
