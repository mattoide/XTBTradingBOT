from statistics import mean
from time import sleep
from tracemalloc import start
from XTBWrapper.xAPIConnector import *
import datetime
import os
from dotenv import load_dotenv
import sys
from utils.symbolConfig import getConfigBySymbol

load_dotenv()

USER_ID = os.getenv('USER_ID')
PASSWORD = os.getenv('PASSWORD')

SYMBOL = sys.argv[1]

values = json.loads(getConfigBySymbol(SYMBOL))

PERIODO_RSI = values['PERIODO_RSI']
MINUTI_TIMESTAMP_GET_CHART = values['MINUTI_TIMESTAMP_GET_CHART']
MINUTI_VALORI_SIMBOLO = values['MINUTI_VALORI_SIMBOLO']

VALORE_ALTO_RSI = values['VALORE_ALTO_RSI']
VALORE_BASSO_RSI = values['VALORE_BASSO_RSI']
PERCENTUALE_STOP_LOSS = values['PERCENTUALE_STOP_LOSS']
VALORE_TRALING_STOP_LOSS = values['VALORE_TRALING_STOP_LOSS'] * 10
VALORE_TRALING_STOP_LOSS_SMALL = VALORE_TRALING_STOP_LOSS - 1 * 10
MAX_STOP_LOSS_EUR = values['MAX_STOP_LOSS_EUR']

TRADE_PRICE = 0.01 #seems doenst change anything
MINIMUM_TP_VALUE = 0.20


def createClient():
    client = APIClient()
    loginResponse = client.execute(loginCommand(userId=USER_ID, password=PASSWORD))

    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))

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
    print(profit)
    while (profit < MAX_STOP_LOSS_EUR):
        percentualeStopLoss = percentualeStopLoss - 0.1
        prezzoChiusura = calculateSLBuyOrSell(cmd, prezzo, precision, percentualeStopLoss)
        profit = getProfitCalculation(symbol, lottoMinimo, cmd, prezzo, prezzoChiusura)
        print(profit)
        sleep(.3)
    return percentualeStopLoss

def calcolaProfitto(symbol, cmd, lotto, prezzoApertura, prezzoAttuale):
    return getProfitCalculation(symbol, lotto, cmd, prezzoApertura, prezzoAttuale)
    

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

    prezziChiusura = []

    # df = pd.read_excel(file_name) #Read Excel file as a DataFrame


    for i in range(PERIODO_RSI+1):
            current = lastChartsInfoReverted[i]
            prezziChiusura.append(current['open'] + current['close'])

    prezziChiusuraReverted = prezziChiusura[::-1]

    # for i in range(len(prezziChiusuraReverted)):
    #     # df['CLOSE'][i] = prezziChiusuraReverted[i]

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

    # print(prezziChiusuraReverted)
    # print("gains", gains)
    # print("losses", losses)
    # print("avg_gain: ", avg_gain)
    # print("avg_loss: ", avg_loss)
   # print("RS:", round(rs,2))

    # print("RSI: ",round(rsi, 2))

    # df.to_excel("COPIARSINEW.xlsx")

    return rsi

client = createClient()
lottoMinimo = getSymbol()['returnData']['lotMin']




while True:

    rsi = calcolaRsi()

    openedTrades = getOpenedTrades()['returnData']

    if(len(openedTrades) <= 0):

        symbolInfo = getSymbol()
        prezzoAcquisto = symbolInfo['returnData']['bid']
        prezzoVendita = symbolInfo['returnData']['ask']
        precision = symbolInfo['returnData']['precision']

        if(rsi<VALORE_BASSO_RSI):
            
            percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.BUY, prezzoVendita, precision)

            logga(AproPosizione="BUY", Per=SYMBOL, AlPrezzo=TRADE_PRICE, SL=round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision), TP=0, Lotto=lottoMinimo)
            order = openTrade(TransactionSide.BUY, SYMBOL, TRADE_PRICE,  round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision) , 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']
        elif(rsi>VALORE_ALTO_RSI):

            percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.SELL, prezzoAcquisto, precision)

            logga(AproPosizione="SELL", Per=SYMBOL, AlPrezzo=TRADE_PRICE, SL=round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision), TP=0, Lotto=lottoMinimo)
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
                print("Profitto", profitto)
                # logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS)
                # modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS)


            if(profitto != None and  openedTrade['offset'] <= 0 and profitto>MINIMUM_TP_VALUE):
                logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS)
                print(modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS))

            if(profitto != None and openedTrade['cmd'] == TransactionSide.BUY and rsi > VALORE_ALTO_RSI and profitto > 0):
                # logga(ChiudoPosizione=openedTrade['order'])
                # closeTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, 0.1, openedTrade['sl'], 0, TransactionType.ORDER_CLOSE, lottoMinimo)
                logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS_SMALL)
                print(modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS_SMALL))

            elif(profitto != None and openedTrade['cmd'] == TransactionSide.SELL and rsi < VALORE_BASSO_RSI  and profitto > 0):
                # logga(ChiudoPosizione=openedTrade['order'])
                # closeTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, 0.1, openedTrade['sl'], 0, TransactionType.ORDER_CLOSE, lottoMinimo)
                logga(ModidicoPosizionePerOrdine=openedTrade['order'], ValoreTailingSL=VALORE_TRALING_STOP_LOSS_SMALL)
                modifyTrade(openedTrade['order'], openedTrade['cmd'], SYMBOL, TRADE_PRICE , openedTrade['sl'], 0, TransactionType.ORDER_MODIFY, lottoMinimo, VALORE_TRALING_STOP_LOSS_SMALL)

        else:
            symbolInfo = getSymbol()
            prezzoAcquisto = symbolInfo['returnData']['bid']
            prezzoVendita = symbolInfo['returnData']['ask']
            precision = symbolInfo['returnData']['precision']

            if(rsi<VALORE_BASSO_RSI):
            
                percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.BUY, prezzoVendita, precision)

                logga(AproPosizione="BUY", Per=SYMBOL, AlPrezzo=TRADE_PRICE, SL=round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision), TP=0, Lotto=lottoMinimo)
                order = openTrade(TransactionSide.BUY, SYMBOL, TRADE_PRICE,  round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision) , 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']
            elif(rsi>VALORE_ALTO_RSI):

                percentualeStopLoss = getCorrectStopLoss(SYMBOL,lottoMinimo,TransactionSide.SELL, prezzoAcquisto, precision)

                logga(AproPosizione="SELL", Per=SYMBOL, AlPrezzo=TRADE_PRICE, SL=round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision), TP=0, Lotto=lottoMinimo)
                order = openTrade(TransactionSide.SELL, SYMBOL, TRADE_PRICE, round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision), 0, TransactionType.ORDER_OPEN, lottoMinimo)['returnData']['order']



    sleep(1)