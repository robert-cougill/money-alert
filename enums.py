import enum


class RequestMethod(enum.Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PATCH = 'PATCH'


class APIClient(enum.Enum):
    BITTREX = 'bittrex'
    BLOCKCHAIN = 'blockchain'
    BLOCKCHAIN_V3 = 'blockchain-v3'
    COINGECKO = 'coingecko'
    ALPHAVANTAGE = 'alpha-vantage'
    METALPRICE = 'metal-price'


class DataInterval(enum.Enum):
    MINUTELY = 'minutely'
    HOURLY = 'hourly'
    DAILY = 'daily'
