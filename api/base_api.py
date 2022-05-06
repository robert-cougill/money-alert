import enums
import init
import json
import requests
import time
import typing
import util


class BaseAPI:
    last_api_call_by_client = {
        enums.APIClient.COINGECKO: round(util.timestamp()),
        enums.APIClient.BITTREX: round(util.timestamp()),
        enums.APIClient.BLOCKCHAIN: round(util.timestamp()),
        enums.APIClient.BLOCKCHAIN_V3: round(util.timestamp()),
        enums.APIClient.YAHOOFINANCE: round(util.timestamp())
    }

    CONST_STATUS_OK = int(200)
    CONST_HTTP_ERROR_CODES = [
        # 429 - Too Many Requests
        int(429),
        # 500 - Internal Server Error
        int(500),
        # 502 - Bad Gateway
        int(502),
        # 503 - Service Unavailable
        int(503),
        # 504 - Gateway Timeout
        int(504),
        # 524 - Cloudflare Gateway Timeout
        int(524)
    ]

    def request_data(self, client: enums.APIClient, endpoint: str, method: enums.RequestMethod = enums.RequestMethod.GET, endpoint_args='', params: typing.Optional[typing.Dict] = None, body: typing.Optional[typing.Dict] = None, use_secondary_url: bool = False):
        base_url = init.config['clients'][client.value]['base_url']

        # region API Rate Limiting
        rate_limit_in_milliseconds = round((60 / init.config['clients'][client.value]['rate_limit_in_secs']) * 1000)
        time_now = round(util.timestamp())
        client_wait_period = self.last_api_call_by_client[client] + rate_limit_in_milliseconds

        if client_wait_period >= time_now:
            time.sleep((client_wait_period - time_now) / 1000)

        self.last_api_call_by_client[client] = round(util.timestamp())
        # endregion API Rate Limiting

        # region Coingecko API
        if client == enums.APIClient.COINGECKO:
            init.logger.debug(f'Coingecko endpoint called: {base_url}/{endpoint} [endpointArgs: {endpoint_args}] [params: {params}]')
            url = self.__build_url(base_url, endpoint, endpoint_args, params)

            response = requests.request(method.value, url, params=None, data=body)
            self.__check_response_code(url, response.status_code)
            if response.status_code in self.CONST_HTTP_ERROR_CODES:
                response = self.__retry_request(method, url, None, None, body)

            return response
        # region Coingecko API

        # region Blockchain API
        if client == enums.APIClient.BLOCKCHAIN or client == enums.APIClient.BLOCKCHAIN_V3:
            init.logger.debug(f'Blockchain endpoint called: {base_url}/{endpoint}')
            url = self.__build_url(base_url, endpoint, endpoint_args, params)

            response = requests.request(method.value, url, params=params)
            self.__check_response_code(url, response.status_code)
            if response.status_code in self.CONST_HTTP_ERROR_CODES:
                response = self.__retry_request(method, url)

            return response
        # region Blockchain API

        # region Bittrex API
        if client == enums.APIClient.BITTREX:
            init.logger.debug(f'Bittrex endpoint called: {base_url}/{endpoint} [endpointArgs: {endpoint_args}] [params: {params}]')
            url = self.__build_url(base_url, endpoint, endpoint_args, params)

            content = ''
            if body:
                content = json.dumps(body)

            content_hash = util.sha512(content)
            timestamp = str(util.timestamp())
            signature_string = ''.join([timestamp, url, method.value, content_hash])
            signature = util.signature(signature_string, init.config['clients'][client.value]['secret'])

            headers = {
                'Api-Timestamp': timestamp,
                'Api-Key': init.config['clients'][client.value]['key'],
                'Content-Type': 'application/json',
                'Api-Content-Hash': content_hash,
                'Api-Signature': signature
            }

            response = requests.request(method.value, url, params=None, headers=headers, data=body)
            self.__check_response_code(url, response.status_code)
            if response.status_code in self.CONST_HTTP_ERROR_CODES:
                response = self.__retry_request(method, url, None, headers, body)

            return response
        # region Bittrex API

        # region Yahoo Finance API
        if client == enums.APIClient.YAHOOFINANCE:
            if use_secondary_url:
                base_url = init.config['clients'][client.value]['base_url_secondary']

            init.logger.debug(f'Yahoo Finance endpoint called: {base_url}/{endpoint}')
            url = self.__build_url(base_url, endpoint, endpoint_args, params)

            headers = {
                'X-API-KEY': init.config['clients'][client.value]['key'],
                'Content-Type': 'application/json',
            }

            response = requests.request(method.value, url, headers=headers)
            self.__check_response_code(url, response.status_code)
            if response.status_code in self.CONST_HTTP_ERROR_CODES:
                response = self.__retry_request(method, url, params, headers)

            return response
        # region Yahoo Finance API

    def __retry_request(self, method: enums.RequestMethod = enums.RequestMethod.GET, url: str = None, params: typing.Optional[typing.Dict] = None, headers: typing.Any = None, body: typing.Optional[typing.Dict] = None):
        for i in range(1, 3):
            init.logger.warning(f'Retrying Request: [{url}]. Retry attempt number: {i}')
            time.sleep(60)

            response = requests.request(method.value, url, params=params, headers=headers, data=body)
            if response.status_code == self.CONST_STATUS_OK:
                return response

        return None

    @staticmethod
    def __build_url(base_url: str, endpoint: str, endpoint_args, params: typing.Optional[typing.Dict] = None) -> str:
        url = base_url + '/' + endpoint + '/' + endpoint_args

        if params is None:
            return url

        append_params = ''
        for key, value in params.items():
            if value is None:
                continue

            if len(append_params) == 0:
                append_params += '?'
            else:
                append_params += '&'

            append_params += util.to_string(key) + '=' + util.to_string(value)

        return url + append_params

    def __check_response_code(self, url: str, response_code: int):
        if response_code != self.CONST_STATUS_OK and response_code not in self.CONST_HTTP_ERROR_CODES:
            init.logger.warning(f'We are receiving a status code that is not being handled. URL: {url} | Response Code: {response_code}')
