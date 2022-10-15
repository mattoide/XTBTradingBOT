from statistics import mean
from time import sleep
from tracemalloc import start
from XTBWrapper.xAPIConnector import *
import datetime
import os
from dotenv import load_dotenv
import sys
from utils.symbolConfig import getConfigBySymbol
import logging
import threading


load_dotenv()

# logger properties
DEBUG = False
logger = logging.getLogger()
FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
logging.basicConfig(format=FORMAT)

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


USER_ID = os.getenv('USER_ID')
PASSWORD = os.getenv('PASSWORD')

SYMBOL = sys.argv[1]

values = json.loads(getConfigBySymbol(SYMBOL))

PERIODO_RSI = values['PERIODO_RSI']
MINUTI_TIMESTAMP_GET_CHART = values['MINUTI_TIMESTAMP_GET_CHART'] + 200 
MINUTI_VALORI_SIMBOLO = values['MINUTI_VALORI_SIMBOLO']

VALORE_ALTO_RSI = values['VALORE_ALTO_RSI']
VALORE_BASSO_RSI = values['VALORE_BASSO_RSI']
VALORE_SCARTO_RSI = 3
PERCENTUALE_STOP_LOSS = values['PERCENTUALE_STOP_LOSS']
VALORE_TRALING_STOP_LOSS = values['VALORE_TRALING_STOP_LOSS'] * 10
VALORE_TRALING_STOP_LOSS_SMALL = VALORE_TRALING_STOP_LOSS - 1 * 10
MAX_STOP_LOSS_EUR = values['MAX_STOP_LOSS_EUR']

TRADE_PRICE = 0.01 #seems doenst change anything
MINIMUM_TP_VALUE = 0.50

logger.debug(f"RSI MIN: {VALORE_BASSO_RSI - VALORE_SCARTO_RSI}")
logger.debug(f"RSI MAX: {VALORE_ALTO_RSI + VALORE_SCARTO_RSI}")

# logger.info(f"\n#########\nApro posizione: BUY\nPer: {SYMBOL}\nSL: {round(23 - (2 * 2)/100, 2)}\nLotto:{3}\n#########")

def createClient():
    client = APIClient()
    loginResponse = client.execute(loginCommand(userId=USER_ID, password=PASSWORD))

    if(loginResponse['status'] == False):
        # print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        logger.error('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        raise Exception('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
    else:
        logger.debug(loginResponse)

    # return client

    # get ssId from login response
    # ssid = loginResponse['streamSessionId']
    # sclient = APIStreamClient(ssId=ssid)

    print(f"######### BOT started for {SYMBOL} #########")
    # logga(PERCENTUALE_STOP_LOSS=PERCENTUALE_STOP_LOSS , VALORE_TRALING_STOP_LOSS=VALORE_TRALING_STOP_LOSS)
    return client


def getSymbol():
    return client.commandExecute('getSymbol', dict(symbol=SYMBOL))


def getSymbolChartInfo(fromTimeStamp):
    return client.commandExecute('getChartLastRequest', dict(info=dict(period=MINUTI_VALORI_SIMBOLO, start=fromTimeStamp, symbol=SYMBOL)))


def getExactPrice(price, digits):
    return price / pow(10, digits)

def isAlRialzo(close):
    if(close > 0): return True
    return False

def getExactClosePrice(price, close, digits):
    return getExactPrice(price, digits) + getExactPrice(close, digits)

def openTrade(transactionType, symbol, price, sl, tp, type, volume):
    return client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=transactionType, symbol=symbol, price=price, sl=sl, tp=tp, type=type, volume=volume)))

def closeTrade(order, transactionType, symbol, price, sl, tp, type, volume):
    return client.commandExecute('tradeTransaction',  dict(tradeTransInfo=dict(cmd=transactionType, order=order, symbol=symbol, price=price, sl=sl, tp=tp, type=type, volume=volume)))

def modifyTrade(order, transactionType, symbol, price, sl, tp, type, volume, trailingStopLoss):
    return client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(order=order, cmd=transactionType, symbol=symbol, price=price, sl=sl, tp=tp, type=type, volume=volume, offset=trailingStopLoss)))

def getOpenedTrades():
    return client.commandExecute('getTrades', dict(openedOnly=True))

def getProfitCalculation(symbol,volume,cmd, openPrice, closePrice):
        return client.commandExecute('getProfitCalculation', dict(symbol=symbol, volume=volume, cmd=cmd, openPrice=openPrice, closePrice=closePrice))['returnData']['profit']

def calculateSLBuyOrSell(cmd, prezzo, precision, prercentualeStopLoss):
    if(cmd == TransactionSide.BUY):
        prezzoChiusura = round(prezzo - (prercentualeStopLoss * prezzo)/100, precision)
    else:
        prezzoChiusura = round(prezzo + (prercentualeStopLoss * prezzo)/100, precision)
    return prezzoChiusura

def getCorrectStopLoss(symbol, lottoMinimo, cmd, prezzo, precision):
    prezzoChiusura = calculateSLBuyOrSell(cmd, prezzo, precision, PERCENTUALE_STOP_LOSS)
    profit = getProfitCalculation(symbol, lottoMinimo, cmd, prezzo, prezzoChiusura)
    percentualeStopLoss = PERCENTUALE_STOP_LOSS
    while (profit < MAX_STOP_LOSS_EUR):
        percentualeStopLoss = percentualeStopLoss - 0.1
        prezzoChiusura = calculateSLBuyOrSell(cmd, prezzo, precision, percentualeStopLoss)
        profit = getProfitCalculation(symbol, lottoMinimo, cmd, prezzo, prezzoChiusura)
        sleep(.3)
    return percentualeStopLoss

def calcolaProfitto(symbol, cmd, lotto, prezzoApertura, prezzoAttuale):
    return getProfitCalculation(symbol, lotto, cmd, prezzoApertura, prezzoAttuale)

def monitoraProfitto():
    while True:
        o = getOpenedTrades()
        # openedTradess = getOpenedTrades()['returnData']
        si = getSymbol()
        pa = si['returnData']['bid']
        pv = si['returnData']['ask']
        lm = getSymbol()['returnData']['lotMin']


        if(len(o['returnData']) > 0):
            print("c equalcosa")
            ot = next((x for x in o['returnData'] if x['symbol'] == SYMBOL), None)
            print(ot)
            if(ot != None):
                pf = calcolaProfitto(SYMBOL, ot['cmd'], lm, ot['open_price'], pa if ot['cmd'] == TransactionSide.BUY else pv)
                logger.info(f"\n#########\nCalculated profit: {pf}\n#########")

            #     if(profitto != None and  openedTrade['offset'] <= 0 and profitto>MINIMUM_TP_VALUE):
            #         logger.info(f"\n#########\nModify position for order {openedTradee['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS}\n#########")
            #         logger.info(modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS))
        logger.info("im THE THREAD")
        sleep(.5)
    

def logga(**data):
    # data is a dict
    for key, value in data.items():
        print(f"{key}: {value}")
    
    print("####################")



def calcolaRsi():

    minfa = datetime.datetime.now() - datetime.timedelta(minutes=MINUTI_TIMESTAMP_GET_CHART)

    minfa = "{:10.3f}".format(minfa.timestamp()).replace('.', '')

    lastChartsGeneralInfo = getSymbolChartInfo(int(minfa))

    lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']

    lastChartsInfoReverted = sorted(lastChartsInfo, key=lambda x: x['ctm'], reverse=True)
    logger.debug (f'LAST CHARTS LENGTH: {len(lastChartsInfoReverted)}')

    prezziChiusura = []

    for i in range(PERIODO_RSI+1):
            current = lastChartsInfoReverted[i]
            prezziChiusura.append(current['open'] + current['close'])

    prezziChiusuraReverted = prezziChiusura[::-1]

    gains = []
    losses = []


    for i in range(PERIODO_RSI):
        difference = prezziChiusuraReverted[i+1] - prezziChiusuraReverted[i]
        if(difference>0):
            gain = difference
            loss = 0
        elif(difference <0):
            gain = 0
            loss = abs(difference)
        else:
            gain = 0
            loss = 0


        gains.append(round(gain,2))
        losses.append(round(loss,2))

    avg_gain = sum(gains) / len(gains)
    avg_loss = sum(losses) / len(losses)

    rs = avg_loss and avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    logger.info (f'RSI: {round(rsi, 2)}')

    return rsi



client = createClient()



lottoMinimo = getSymbol()['returnData']['lotMin']
x = threading.Thread(target=monitoraProfitto)
x.daemon = True
x.start()

while True:

    rsi = calcolaRsi()

    openedTrades = getOpenedTrades()['returnData']

    if(len(openedTrades) <= 0):

        symbolInfo = getSymbol()
        prezzoAcquisto = symbolInfo['returnData']['bid']
        prezzoVendita = symbolInfo['returnData']['ask']
        precision = symbolInfo['returnData']['precision']

        if(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI))):
            
            percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.BUY, prezzoVendita, precision)

            logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision)}\nLot:{lottoMinimo}\n#########")
            order = openTrade(TransactionSide.BUY, SYMBOL, TRADE_PRICE,  round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision) , 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']
        if(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI))):

            percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.SELL, prezzoAcquisto, precision)

            logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision)}\nLot:{lottoMinimo}\n#########")
            order = openTrade(TransactionSide.SELL, SYMBOL, TRADE_PRICE, round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision), 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']

    else:
        openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None)

        if(openedTrade != None):

            profitto = openedTrade['profit']
            
            if(profitto == None):
                symbolInfo = getSymbol()
                prezzoAcquisto = symbolInfo['returnData']['bid']
                prezzoVendita = symbolInfo['returnData']['ask']
                
                profitto = calcolaProfitto(SYMBOL, openedTrade['cmd'], lottoMinimo, openedTrade['open_price'], prezzoAcquisto if openedTrade['cmd'] == TransactionSide.BUY else prezzoVendita)
                logger.info(f"\n#########\nError retrieving profit. Calculated profit: {profitto}\n#########")

                # logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS)
                # modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS)


            if(profitto != None and  openedTrade['offset'] <= 0 and profitto>MINIMUM_TP_VALUE):

                logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS}\n#########")
                logger.info(modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS))

            # if(profitto != None and openedTrade['cmd'] == TransactionSide.BUY and rsi > VALORE_ALTO_RSI and profitto > 0):
            #     # logga(ChiudoPosizione=openedTrade['order'])
            #     # closeTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, 0.1, openedTrade['sl'], 0, TransactionType.ORDER_CLOSE, lottoMinimo)
            #     logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS_SMALL)
            #     print(modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS_SMALL))

            # elif(profitto != None and openedTrade['cmd'] == TransactionSide.SELL and rsi < VALORE_BASSO_RSI  and profitto > 0):
            #     # logga(ChiudoPosizione=openedTrade['order'])
            #     # closeTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, 0.1, openedTrade['sl'], 0, TransactionType.ORDER_CLOSE, lottoMinimo)
            #     logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS_SMALL)
            #     modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS_SMALL)

        else:
            symbolInfo = getSymbol()
            prezzoAcquisto = symbolInfo['returnData']['bid']
            prezzoVendita = symbolInfo['returnData']['ask']
            precision = symbolInfo['returnData']['precision']

            if(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI))):
            
                percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.BUY, prezzoVendita, precision)

                logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision)}\nLot: {lottoMinimo}\n#########")
                order = openTrade(TransactionSide.BUY, SYMBOL, TRADE_PRICE,  round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision) , 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']
            elif(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI))):

                percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.SELL, prezzoAcquisto, precision)

                logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision)}\nLot: {lottoMinimo}\n#########")
                order = openTrade(TransactionSide.SELL, SYMBOL, TRADE_PRICE, round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision), 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']



    sleep(1)