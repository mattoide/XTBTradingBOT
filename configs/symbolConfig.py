import json
from .logginConfig import logger
from utils.systemUtils import waitForClose


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
            'symbol': "BITCOIN",
            'config':
            
                {

                }
        },      
          {
            'symbol': "EURUSD",
            'config':
            
                {

                }
        },
        {
            'symbol': "USDCHF",
            'config':
                {
                
                }
        },
        {
            'symbol': "GBPCHF",
            'config':

                {
                
                }
            
        },
        {
            'symbol': "GBPUSD",
            'config':
                {
                 
                }
        },
        {
            'symbol': "USDCAD",
            'config':
                {
                  
                }
        },
         {
            'symbol': "EURJPY",
            'config':
                {
                  
                }
        },
         {
            'symbol': "GBPJPY",
            'config':
                {
                  
                }
        },      

    ]