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

# PERIODO_TREND = 10
CHECK_LAST_LAST = False

class XTBot:
    def __init__(self, symbol, autostart=True):
        self.symbol = symbol
        self.checkSymbolConfig()
        self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART
        self.minimum_tp_value = MINIMUM_TP_VALUE * MULTYPLIER
        self.client = APIClient()
        self.login()
        self.symbolInfo = self.getSymbol()
        self.lotMin = self.symbolInfo['returnData']['lotMin'] * MULTYPLIER
        self.previousRsi = 0
        logger.debug(autostart)
        if(autostart):
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

    def calculateSLBuyOrSell(self, cmd, prezzo, precision, pips):
        if(cmd == TransactionSide.BUY):
            prezzoChiusura = round(prezzo - pips, precision)
        else:
            prezzoChiusura = round(prezzo + pips, precision)
        
        return prezzoChiusura

    def getCorrectStopLoss(self, cmd, prezzo, precision):
        logger.debug("Prezzo apertura:", prezzo)
        logger.debug("Cmd:", cmd)
        logger.debug("Precision:", precision)
        prezzoChiusura = self.calculateSLBuyOrSell(cmd, prezzo, precision, round(PIPS_STOP_LOSS / pow(10, precision)))
        perdita = self.getProfitCalculation(cmd, prezzo, prezzoChiusura)
        pips = round(PIPS_STOP_LOSS / pow(10, precision), precision)
        while (perdita > MAX_STOP_LOSS_EUR):
            pips = pips * 1.3
            prezzoChiusura = self.calculateSLBuyOrSell(cmd, prezzo, precision, pips)
            perdita = self.getProfitCalculation(cmd, prezzo, prezzoChiusura)
            sleep(.3)
        
        # print(round(pips,precision))
        return pips

    def calcolaProfitto(self, cmd, prezzoApertura, prezzoAttuale):
        return self.getProfitCalculation(cmd, prezzoApertura, prezzoAttuale)

    def checkRSIIfInBuyRange(self, rsi):
        return(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)))
                    

    def checkRSIIfInSellRange(self, rsi):
        return(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)))
    
    def checkIfLastTradeIsOk(self, cmd):
        yesterady = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterady = "{:10.3f}".format(yesterady.timestamp()).replace('.', '')
        print(yesterady)
        trades = self.client.commandExecute('getTradesHistory', dict(end=0, start=int(yesterady)))['returnData']
        # trades = trades[::-1]
        trade = next((x for x in trades if x['symbol'] == SYMBOL and x['cmd'] == cmd), None) if len(trades) > 0 else None
        print("ID ULTIMA TRANSAZIONE:", trade['position'])

        if(trade != None):
            if(trade['profit'] > 0):
                return True
            else:
                return False
        else:
            return True



    def calcolaRsi(self):

        minutesAgo = datetime.datetime.now() - datetime.timedelta(minutes=self.minuti_timestamp_get_charts)

        minutesAgo = "{:10.3f}".format(minutesAgo.timestamp()).replace('.', '')

        lastChartsGeneralInfo = self.getSymbolChartInfo(int(minutesAgo))

        lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']

        while len(lastChartsInfo) < (PERIODO_RSI + 1):
            self.minuti_timestamp_get_charts = self.minuti_timestamp_get_charts * 2
            minutesAgo = datetime.datetime.now() - datetime.timedelta(minutes=self.minuti_timestamp_get_charts)
            minutesAgo = "{:10.3f}".format(minutesAgo.timestamp()).replace('.', '')
            lastChartsGeneralInfo = self.getSymbolChartInfo(int(minutesAgo))
            lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']

            sleep(.3)

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

        logger.debug(f'RSI {PERIODO_RSI} PERIODI: {round(rsi, 2)}')
        # print(f'RSI 14 : {round(rsi, 2)}')

        if(prezziChiusuraReverted[len(prezziChiusuraReverted)-1] > prezziChiusuraReverted[len(prezziChiusuraReverted)-2]):
            self.rialzo = True
            logger.debug(f"{prezziChiusuraReverted[len(prezziChiusuraReverted)-1]} > {prezziChiusuraReverted[len(prezziChiusuraReverted)-2]}")
        else:
            self.rialzo = False
            logger.debug(f"{prezziChiusuraReverted[len(prezziChiusuraReverted)-1]} < {prezziChiusuraReverted[len(prezziChiusuraReverted)-2]}")


        return rsi
    
    def makeSomeMoney(self):
        while True:

            rsi = self.calcolaRsi()
            # rsi = self.calcolaRsi7Periodi()

            openedTrades = self.getOpenedTrades()['returnData']

            openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None) if len(openedTrades) > 0 else None

            # if(openedTrade != None):
            #     print(f"OPENED TRADE {openedTrade['symbol']}")
            # else:
            #     print("TRADE NON TROVATO")
            # print("Lunghezza trades:", len(openedTrades))

            if(len(openedTrades) <= 0 or openedTrade == None):

                logger.debug("Non ho trade aperti oppure non trovo un trade con qursto symbol")
                logger.debug("RSI:", round(rsi,2))
                logger.debug(f"RSI:{int(rsi)} BASSO: {int(VALORE_BASSO_RSI)} SCARTO: {int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)}")
                logger.debug(f"RSI:{int(rsi)} ALTO: {int(VALORE_ALTO_RSI)} SCARTO: {int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)}")
                symbolInfo = self.getSymbol()
                prezzoAcquisto = symbolInfo['returnData']['bid']
                prezzoVendita = symbolInfo['returnData']['ask']
                precision = symbolInfo['returnData']['precision']

                logger.debug("previuoso rsi", self.previousRsi)
                logger.debug("Currrenti rsi", rsi)
                logger.debug("\n\n")


                # if((self.checkRSIIfInBuyRange(rsi) and self.rialzo == True) or (self.previousRsi != 0 and rsi > self.previousRsi and self.rialzo == True)):
                #     print("DOVREI COMPRARE")

                # if((self.checkRSIIfInSellRange(rsi)     and self.rialzo == False) or (self.previousRsi != 0 and rsi < self.previousRsi and self.rialzo == False)):
                #     print("DOVREI VENDERE")
                
                # self.previousRsi = rsi

                # if(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)) and self.rialzo == True):
                if((self.checkRSIIfInBuyRange(rsi) and self.rialzo == True) or (self.previousRsi != 0 and rsi > self.previousRsi and self.rialzo == True)):
                    if self.checkIfLastTradeIsOk(TransactionSide.BUY):
                        logger.info("Ultimo BUY OK quindi compro perche dovrei comprare")
                        
                        pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
                        sl = round(prezzoVendita - pips, precision)

                        logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                        self.openBuyTrade(sl, 0)
                    else:
                        if(not CHECK_LAST_LAST):
                                logger.info("VENDO perche ultimo trade in BUY è andato male")

                                pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
                                sl = round(prezzoAcquisto + pips, precision)

                                logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                                self.openSellTrade(sl, 0)
                        else:
                            
                            if self.checkIfLastTradeIsOk(TransactionSide.SELL):
                                logger.info("VENDO perche ultimo trade in BUY è andato male")

                                pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
                                sl = round(prezzoAcquisto + pips, precision)

                                logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                                self.openSellTrade(sl, 0)
                            else:
                                logger.debug("mi trovo nel range BUY")
                                logger.info("Ultimo BUY KO quindi dovrei vendere ma ULTIMO SELL KO quindi COMPRO")

                                pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
                                sl = round(prezzoVendita - pips, precision)

                                logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                                self.openBuyTrade(sl, 0)                           
               
                # if(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)) and self.rialzo == False):
                if((self.checkRSIIfInSellRange(rsi)and self.rialzo == False) or (self.previousRsi != 0 and rsi < self.previousRsi and self.rialzo == False)):
                    if self.checkIfLastTradeIsOk(TransactionSide.SELL):

                        logger.debug("mi trovo nel range SELL")

                        pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
                        sl = round(prezzoAcquisto + pips, precision)

                        logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                        self.openSellTrade(sl, 0)
                    else:
                        if(not CHECK_LAST_LAST):

                            logger.info("COMPRO perche ultimo trade in SELL è andato male")
                            pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
                            sl = round(prezzoVendita - pips, precision)

                            logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                            self.openBuyTrade(sl, 0)

                        else:
                                
                            if self.checkIfLastTradeIsOk(TransactionSide.BUY):

                                logger.info("COMPRO perche ultimo trade in SELL è andato male")
                                pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
                                sl = round(prezzoVendita - pips, precision)

                                logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                                self.openBuyTrade(sl, 0)
                            else:

                                logger.debug("mi trovo nel range SELL")

                                pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
                                sl = round(prezzoAcquisto + pips, precision)

                                logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{rsi}\n#########")

                                self.openSellTrade(sl, 0)
                    
                self.previousRsi = rsi

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


                    # print(f'RSI: {round(rsi, 2)} - Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'RSI: {round(rsi, 2)} -Profit: {RED} {profitto} {RESET}      ',end="\r")
                    print(f'Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'Profit: {RED} {profitto} {RESET}      ',end="\r")
                    
                    if(profitto != None and  openedTrade['offset'] <= 0 and profitto>self.minimum_tp_value):

                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS)['status']
                        
                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")

                  
            sleep(1)

    

print(f"######### BOT started for {SYMBOL} #########")

try:
    xtbot = XTBot(SYMBOL)
except Exception as e:
    logger.info(f"{e}")
    waitForClose()
