import json

VALORE_RSI_MEDIO = 50

def getConfigBySymbol(symbol):
    match symbol:
        case "EURUSD":
            return json.dumps({
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
                'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
                'PERCENTUALE_STOP_LOSS' : 1,
                'VALORE_TRALING_STOP_LOSS' : 20,
                'MAX_STOP_LOSS_EUR': -5
            })
        case "BITCOIN":
            return json.dumps({
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
                'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
                'PERCENTUALE_STOP_LOSS' : 1,
                'VALORE_TRALING_STOP_LOSS' : 20,
                'MAX_STOP_LOSS_EUR': -5
            })
        case "USDCHF":
            return json.dumps({
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
                'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
                'PERCENTUALE_STOP_LOSS' : 1,
                'VALORE_TRALING_STOP_LOSS' : 20,
                'MAX_STOP_LOSS_EUR': -5
            })
        case "GBPCHF":
            return json.dumps({
                'PERIODO_RSI' : 14,
                'MINUTI_TIMESTAMP_GET_CHART' : 20,
                'MINUTI_VALORI_SIMBOLO' : 1,
                'VALORE_ALTO_RSI' : VALORE_RSI_MEDIO + 20,
                'VALORE_BASSO_RSI' : VALORE_RSI_MEDIO - 20,
                'PERCENTUALE_STOP_LOSS' : 1,
                'VALORE_TRALING_STOP_LOSS' : 20,
                'MAX_STOP_LOSS_EUR': -5
            })
        case _:
            raise Exception("Nessuna configurazione presente per asset:", symbol)

