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
    YAHOOFINANCE = 'yahoo-finance'


class DataInterval(enum.Enum):
    MINUTELY = 'minutely'
    HOURLY = 'hourly'
    DAILY = 'daily'


class YahooDataTimePeriod(enum.Enum):
    ONE_DAY = '1D'
    FIVE_DAY = '5D'
    ONE_MONTH = '1M'
    THREE_MONTH = '3M'
    SIX_MONTH = '6M'
    ONE_YEAR = '1Y'
    FIVE_YEAR = '5Y'
