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


PERIODO_CHARTS = 1
MINIMUM_TP_VALUE = 0.10
MULTYPLIER = 1

VALORE_TRALING_STOP_LOSS_ALTO = 1 * 10
VALORE_TRALING_STOP_LOSS_BASSO = 2 * 10

DIVISORE_GRANDEZZA_CANDELA = 2

PERIODO_RSI = 14
VALORE_RSI_MEDIO = 50
VALORE_ALTO_RSI = VALORE_RSI_MEDIO + 15
VALORE_BASSO_RSI = VALORE_RSI_MEDIO - 15

MINUTI_TIMESTAMP_GET_CHART_1_MIN = 20
MINUTI_TIMESTAMP_GET_CHART_5_MIN = 80

VALORE_SCARTO_RSI = 5

PIPS_STOP_LOSS = 1 #TODO: DA VEDERE



# MAX_STOP_LOSS_EUR = values['MAX_STOP_LOSS_EUR'] #TODO: inutile se piazzo sl su resistenze ecc
# MAX_STOP_LOSS_EUR = -0.5
# MAX_STOP_LOSS_EUR_FOREX = -0.80
# MAX_STOP_LOSS_EUR_CRYPTO = -1

TRADE_PRICE = 0.01 #seems doenst change anything






