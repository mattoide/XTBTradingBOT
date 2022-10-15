import sys
from time import sleep
from XTBWrapper.xAPIConnector import APIClient, loginCommand, TransactionSide, TransactionType
from configs.logginConfig import logger
from configs.userConfigs import USER_ID, PASSWORD
from configs.tradingConfig import *
from configs.generalConfigs import *
from configs.symbolConfig import getConfigBySymbol
from utils.systemUtils import waitForClose
import datetime


SYMBOL = sys.argv[1]

class XTBot:
    def __init__(self, symbol):
        self.symbol = symbol
        self.checkSymbolConfig()
        self.client = APIClient()
        self.login()
        self.symbolInfo = self.getSymbol()
        self.lotMin = self.symbolInfo['returnData']['lotMin'] * MULTYPLIER
        self.makeSomeMoney()
    
    def login(self):
            loginResponse = self.client.execute(loginCommand(userId=USER_ID, password=PASSWORD))
            if(loginResponse['status'] == False):
                raise Exception('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
            else:
                logger.debug(loginResponse)

    

    def checkSymbolConfig(self):
        getConfigBySymbol(self.symbol)

    def getSymbol(self):
        return self.client.commandExecute('getSymbol', dict(symbol=self.symbol))


    def getSymbolChartInfo(self, fromTimeStamp):
        return self.client.commandExecute('getChartLastRequest', dict(info=dict(period=MINUTI_VALORI_SIMBOLO, start=fromTimeStamp, symbol=SYMBOL)))


    # def getExactClosePrice(price, close, digits):
    #     return getExactPrice(price, digits) + getExactPrice(close, digits)

    def openBuyTrade(self, sl, tp):
        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.BUY, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=tp, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']

    def openSellTrade(self, sl, tp):
        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.SELL, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=tp, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']

    def modifyTrade(self, order, transactionType, sl, tp, trailingStopLoss):
        return self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(order=order, cmd=transactionType, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=tp, type=TransactionType.ORDER_MODIFY, volume=self.lotMin, offset=trailingStopLoss)))

    def getOpenedTrades(self):
        return self.client.commandExecute('getTrades', dict(openedOnly=True))

    def getProfitCalculation(self, cmd, openPrice, closePrice):
        return self.client.commandExecute('getProfitCalculation', dict(symbol=SYMBOL, volume=self.lotMin, cmd=cmd, openPrice=openPrice, closePrice=closePrice))['returnData']['profit']

    def calculateSLBuyOrSell(cmd, prezzo, precision, prercentualeStopLoss):
        if(cmd == TransactionSide.BUY):
            prezzoChiusura = round(prezzo - (prercentualeStopLoss * prezzo)/100, precision)
        else:
            prezzoChiusura = round(prezzo + (prercentualeStopLoss * prezzo)/100, precision)
        return prezzoChiusura

    def getCorrectStopLoss(self, cmd, prezzo, precision):
        prezzoChiusura = self.calculateSLBuyOrSell(cmd, prezzo, precision, PERCENTUALE_STOP_LOSS)
        profit = self.getProfitCalculation(SYMBOL, self.lotMin, cmd, prezzo, prezzoChiusura)
        percentualeStopLoss = PERCENTUALE_STOP_LOSS

        while (profit < MAX_STOP_LOSS_EUR):
            percentualeStopLoss = percentualeStopLoss - 0.1
            prezzoChiusura = self.calculateSLBuyOrSell(cmd, prezzo, precision, percentualeStopLoss)
            profit = self.getProfitCalculation(SYMBOL, self.lotMin, cmd, prezzo, prezzoChiusura)
            sleep(.3)

        return percentualeStopLoss

    def calcolaProfitto(self, cmd, prezzoApertura, prezzoAttuale):
        return self.getProfitCalculation(SYMBOL, self.lotMin, cmd, prezzoApertura, prezzoAttuale)

    def calcolaRsi(self):

        minutesAgo = datetime.datetime.now() - datetime.timedelta(minutes=MINUTI_TIMESTAMP_GET_CHART)

        minutesAgo = "{:10.3f}".format(minutesAgo.timestamp()).replace('.', '')

        lastChartsGeneralInfo = self.getSymbolChartInfo(int(minutesAgo))

        lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']

        lastChartsInfoReverted = sorted(lastChartsInfo, key=lambda x: x['ctm'], reverse=True)

        logger.debug(f'LAST CHARTS LENGTH: {len(lastChartsInfoReverted)}')

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

        logger.debug (f'RSI: {round(rsi, 2)}')

        return rsi
    
    def makeSomeMoney(self):
        while True:

            rsi = self.calcolaRsi()

            openedTrades = self.getOpenedTrades()['returnData']

            openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None) if len(openedTrades) > 0 else None

            if(len(openedTrades) <= 0 and openedTrade == None):

                logger.debug("Non ho trade aperti oppure non trovo un trade con qursto symbol")

                symbolInfo = self.getSymbol()
                prezzoAcquisto = symbolInfo['returnData']['bid']
                prezzoVendita = symbolInfo['returnData']['ask']
                precision = symbolInfo['returnData']['precision']

                if(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI))):
                    
                    percentualeStopLoss = self.getCorrectStopLoss(SYMBOL,self.lotMin,TransactionSide.BUY, prezzoVendita, precision)
                    sl = round(prezzoVendita - (percentualeStopLoss * prezzoVendita)/100, precision)

                    logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\n#########")

                    self.openBuyTrade(sl, 0)
               
                if(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI))):

                    percentualeStopLoss = self.getCorrectStopLoss(SYMBOL,self.lotMin,TransactionSide.SELL, prezzoAcquisto, precision)
                    sl = round(prezzoAcquisto + (percentualeStopLoss * prezzoAcquisto)/100, precision)

                    logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\n#########")

                    self.openSellTrade(sl, 0)
            else:
                # openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None)
                
                logger.debug("esiste un trade con questo symbol")

                if(openedTrade != None):

                    profitto = openedTrade['profit']
                    
                    if(profitto == None):
                        symbolInfo = self.getSymbol()
                        prezzoAcquisto = symbolInfo['returnData']['bid']
                        prezzoVendita = symbolInfo['returnData']['ask']
                        
                        profitto = self.calcolaProfitto(openedTrade['cmd'], openedTrade['open_price'], prezzoAcquisto if openedTrade['cmd'] == TransactionSide.BUY else prezzoVendita)
                        logger.info(f"\n#########\nError retrieving profit. Calculated profit: {profitto}\n#########")


                    print(f'Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'Profit: {RED} {profitto} {RESET}      ',end="\r")
                    
                    if(profitto != None and  openedTrade['offset'] <= 0 and profitto>MINIMUM_TP_VALUE):

                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS)['status']
                        
                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")

                  
            sleep(1)


print(f"######### BOT started for {SYMBOL} #########")

try:
    xtbot = XTBot(SYMBOL)
except Exception as e:
    logger.error(e)
    waitForClose()
