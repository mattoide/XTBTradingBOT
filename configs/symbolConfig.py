import json
from .logginConfig import logger
from utils.systemUtils import waitForClose

VALORE_RSI_MEDIO = 50
VALORE_ALTO_RSI = VALORE_RSI_MEDIO + 20
VALORE_BASSO_RSI = VALORE_RSI_MEDIO - 20
MAX_STOP_LOSS_EUR = -2
VALORE_TRALING_STOP_LOSS = 4
PIPS_STOP_LOSS = 1

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
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
        {
            'symbol': "BITCOIN",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
        {
            'symbol': "USDCHF",
            'config':
                {
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
        {
            'symbol': "GBPCHF",
            'config':

                {
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
            
        },
        {
            'symbol': "GBPUSD",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
        {
            'symbol': "USDCAD",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
         {
            'symbol': "EURJPY",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
         {
            'symbol': "GBPJPY",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },         {
            'symbol': "TSLA.US_4",
            'config':
                {
                    'PERIODO_RSI' : 14,
                    'MINUTI_TIMESTAMP_GET_CHART' : 20,
                    'MINUTI_VALORI_SIMBOLO' : 1,
                    'VALORE_ALTO_RSI' : VALORE_ALTO_RSI,
                    'VALORE_BASSO_RSI' : VALORE_BASSO_RSI,
                    'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
                    'VALORE_TRALING_STOP_LOSS' : VALORE_TRALING_STOP_LOSS,
                    'MAX_STOP_LOSS_EUR': MAX_STOP_LOSS_EUR
                }
        },
  
    ]



    # match symbol:
    #     case "EURUSD":
    #         return json.dumps({
    #             'PERIODO_RSI' : 14,
    #             'MINUTI_TIMESTAMP_GET_CHART' : 20,
    #             'MINUTI_VALORI_SIMBOLO' : 1,
    #             'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
    #             'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
    #             'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
    #             'VALORE_TRALING_STOP_LOSS' : 2,
    #             'MAX_STOP_LOSS_EUR': -5
    #         })
    #     case "BITCOIN":
    #         return json.dumps({
    #             'PERIODO_RSI' : 14,
    #             'MINUTI_TIMESTAMP_GET_CHART' : 20,
    #             'MINUTI_VALORI_SIMBOLO' : 1,
    #             'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
    #             'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
    #             'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
    #             'VALORE_TRALING_STOP_LOSS' : 2,
    #             'MAX_STOP_LOSS_EUR': -5
    #         })
    #     case "USDCHF":
    #         return json.dumps({
    #             'PERIODO_RSI' : 14,
    #             'MINUTI_TIMESTAMP_GET_CHART' : 20,
    #             'MINUTI_VALORI_SIMBOLO' : 1,
    #             'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
    #             'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
    #             'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
    #             'VALORE_TRALING_STOP_LOSS' : 2,
    #             'MAX_STOP_LOSS_EUR': -5
    #         })
    #     case "GBPCHF":
    #         return json.dumps({
    #             'PERIODO_RSI' : 14,
    #             'MINUTI_TIMESTAMP_GET_CHART' : 20,
    #             'MINUTI_VALORI_SIMBOLO' : 1,
    #             'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
    #             'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
    #             'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
    #             'VALORE_TRALING_STOP_LOSS' : 2,
    #             'MAX_STOP_LOSS_EUR': -5
    #         })
    #     case "GBPUSD":
    #         return json.dumps({
    #             'PERIODO_RSI' : 14,
    #             'MINUTI_TIMESTAMP_GET_CHART' : 20,
    #             'MINUTI_VALORI_SIMBOLO' : 1,
    #             'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
    #             'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
    #             'PIPS_STOP_LOSS' : PIPS_STOP_LOSS,
    #             'VALORE_TRALING_STOP_LOSS' : 2,
    #             'MAX_STOP_LOSS_EUR': -5
    #         })
    #     case _:
    #         raise Exception("Nessuna configurazione presente per asset:", symbol)

