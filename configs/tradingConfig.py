import sys
import json
from .symbolConfig import getConfigBySymbol
from .logginConfig import logger
from utils.systemUtils import waitForClose

SYMBOL = sys.argv[1]

try:
    values = json.loads(getConfigBySymbol(SYMBOL))
except Exception as e:
    logger.error(e)
    waitForClose()


PERIODO_RSI = values['PERIODO_RSI']
MINUTI_TIMESTAMP_GET_CHART = values['MINUTI_TIMESTAMP_GET_CHART']
MINUTI_VALORI_SIMBOLO = values['MINUTI_VALORI_SIMBOLO']

VALORE_ALTO_RSI = values['VALORE_ALTO_RSI']
VALORE_BASSO_RSI = values['VALORE_BASSO_RSI']
VALORE_SCARTO_RSI = 5
PIPS_STOP_LOSS = values['PIPS_STOP_LOSS']
VALORE_TRALING_STOP_LOSS = values['VALORE_TRALING_STOP_LOSS'] * 10
VALORE_TRALING_STOP_LOSS_SMALL = VALORE_TRALING_STOP_LOSS - 1 * 10
MAX_STOP_LOSS_EUR = values['MAX_STOP_LOSS_EUR']

TRADE_PRICE = 0.01 #seems doenst change anything
MINIMUM_TP_VALUE = 0.50
MULTYPLIER = 1