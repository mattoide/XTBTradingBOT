import json
from .logginConfig import logger
from utils.systemUtils import waitForClose

VALORE_RSI_MEDIO = 50
VALORE_ALTO_RSI = VALORE_RSI_MEDIO + 10
VALORE_BASSO_RSI = VALORE_RSI_MEDIO - 10
MAX_STOP_LOSS_EUR_FOREX = -0.80
MAX_STOP_LOSS_EUR_CRYPTO = -1
VALORE_TRALING_STOP_LOSS_ALTO = 1
VALORE_TRALING_STOP_LOSS_BASSO = 3
PIPS_STOP_LOSS = 1
PERIODO_CHARTS = 1

def getConfigBySymbol(symbol):
    symb = next((x for x in symbols if x["symbol"] == symbol), None)
    if(symb != None):
        return json.dumps(symb['config'])
    else:
        raise Exception("Nessuna configurazione presente per asset:", symbol)

def getAllSymbols():
    return json.dumps(symbols)

 
symbols =    [
        {
            'symbol': "EURUSD",
            'config':
            
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },
        {
            'symbol': "BITCOIN",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_CRYPTO
                }
        },
        {
            'symbol': "USDCHF",
            'config':
                {
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'PERIODO_CHARTS' : PERIODO_CHARTS,
                'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },
        {
            'symbol': "GBPCHF",
            'config':

                {
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'PERIODO_CHARTS' : PERIODO_CHARTS,
                'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
            
        },
        {
            'symbol': "GBPUSD",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },
        {
            'symbol': "USDCAD",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },
         {
            'symbol': "EURJPY",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },
         {
            'symbol': "GBPJPY",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'PERIODO_CHARTS' : PERIODO_CHARTS,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS_ALTO' : VALORE_TRALING_STOP_LOSS_ALTO,
                    'VALORE_TRALING_STOP_LOSS_BASSO' : VALORE_TRALING_STOP_LOSS_BASSO,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR_FOREX
                }
        },      

    ]