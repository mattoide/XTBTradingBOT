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
from tests.testplot import plotta, getCharts


SYMBOL = sys.argv[1]

class XTBot:
    def __init__(self, symbol, autostart=True):
        self.symbol = symbol
        self.checkSymbolConfig()
        self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART_1_MIN
        self.minimum_tp_value = MINIMUM_TP_VALUE * MULTYPLIER
        self.stopLoss = 0
        self.client = APIClient()
        self.login()
        self.symbolInfo = self.getSymbol()
        self.lotMin = self.symbolInfo['returnData']['lotMin'] * MULTYPLIER
        self.precision = self.symbolInfo['returnData']['precision']
        self.pipsPrecision = self.symbolInfo['returnData']['pipsPrecision']
        self.previousRsi = 0
        print(f"######### BOT started for {SYMBOL} #########")
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


    def getSymbolChartInfo(self, fromTimeStamp, period):
        return self.client.commandExecute('getChartLastRequest', dict(info=dict(period=period, start=fromTimeStamp, symbol=SYMBOL)))


    # def getExactClosePrice(price, close, digits):
    #     return getExactPrice(price, digits) + getExactPrice(close, digits)

    # def openBuyTrade(self):

    #     symbolInfo = self.getSymbol()
    #     prezzoVendita = symbolInfo['returnData']['ask']
    #     precision = symbolInfo['returnData']['precision']
    #     pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
    #     sl = round(prezzoVendita - pips, precision)

    #     logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

    #     order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.BUY, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
    #     if(order['status']):
    #         self.order = order['returnData']['order']
    #     else:
    #         print("ERROR: ",order)

    # def openSellTrade(self):

    #     symbolInfo = self.getSymbol()
    #     prezzoAcquisto = symbolInfo['returnData']['bid']
    #     precision = symbolInfo['returnData']['precision']
    #     pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
    #     sl = round(prezzoAcquisto + pips, precision)

    #     logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

    #     order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.SELL, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
    #     if(order['status']):
    #         self.order = order['returnData']['order']
    #     else:
    #         print("ERROR: ",order)

    def openBuyTradeInversion(self, sl):

        logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.BUY, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']
        else:
            print("ERROR: ",order)

    def openSellTradeInversion(self, sl):

        logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.SELL, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']
        else:
            print("ERROR: ",order)

    def modifyTrade(self, order, transactionType, sl, tp, trailingStopLoss):
        return self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(order=order, cmd=transactionType, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=tp, type=TransactionType.ORDER_MODIFY, volume=self.lotMin, offset=trailingStopLoss)))

    def getOpenedTrades(self):
        return self.client.commandExecute('getTrades', dict(openedOnly=True))

    def getProfitCalculation(self, cmd, openPrice, closePrice):
        return self.client.commandExecute('getProfitCalculation', dict(symbol=SYMBOL, volume=self.lotMin, cmd=cmd, openPrice=openPrice, closePrice=closePrice))['returnData']['profit']

    # def calculateSLBuyOrSell(self, cmd, prezzo, precision, pips):
    #     if(cmd == TransactionSide.BUY):
    #         prezzoChiusura = round(prezzo - pips, precision)
    #     else:
    #         prezzoChiusura = round(prezzo + pips, precision)

    #     return prezzoChiusura

    # def getCorrectStopLoss(self, cmd, prezzo, precision):
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
        return(int(rsi) < (int(VALORE_BASSO_RSI)))


    def checkRSIIfInSellRange(self, rsi):
        return(int(rsi) > (int(VALORE_ALTO_RSI)))

    def exactPrice(self, price):
        return price / pow(10, self.precision)

    def chiusura(self, candle):
        return (candle['open'] + candle['close']) / pow(10, self.precision)

    def highPrice(self, candle):
        return (candle['open'] + candle['high']) / pow(10, self.precision)

    def lowPrice(self, candle):
        return (candle['open'] + candle['low']) / pow(10, self.precision)

    def isStar(self, candle):
        if(candle['close'] >= 0 ):
            if((self.highPrice(candle) - self.chiusura(candle)) > (self.exactPrice(candle['open']) - self.lowPrice(candle)) * DIVISORE_GRANDEZZA_CANDELA):
                return True
        else:
             if((self.highPrice(candle) - self.exactPrice(candle['open'])) > (self.exactPrice(candle['open']) - self.lowPrice(candle)) *  DIVISORE_GRANDEZZA_CANDELA):
                return True    
        
        self.stopLoss = self.highPrice(candle)
        return False       

    def isHammer(self, candle):
        if(candle['close'] >= 0 ):
            if((self.exactPrice(candle['open']) - self.lowPrice(candle)) > (self.highPrice(candle) - self.chiusura(candle)) * DIVISORE_GRANDEZZA_CANDELA):
                return True
        else:
            if((self.chiusura(candle) - self.lowPrice(candle)) > (self.highPrice(candle) - self.exactPrice(candle['open'])) * DIVISORE_GRANDEZZA_CANDELA):
                return True    

        self.stopLoss = self.lowPrice(candle)
        return False   

    
    def distanzaTraAperturaEChiusura(self, candle):
        return abs(self.chiusura(candle) - self.exactPrice(candle['open']))

    def candela1InghiotteCandela2(self, candle1, candle2):
        return self.highPrice(candle1) > self.highPrice(candle2) and self.lowPrice(candle1) < self.lowPrice(candle2)

    def isGreen(self, candle):
        return candle['close'] >= 0

    def isRed(self, candle):
        return candle['close'] < 0
    
    def isBullishEngulfingFigure(self, candle1, candle2):
        if(self.isGreen(candle1) and self.isRed(candle2) and  self.chiusura(candle1) > self.chiusura(candle2) and self.candela1InghiotteCandela2(candle1, candle2)):
            print("PATTERN isBullishEngulfingFigure")
            print("Candela 1 orario:", candle1['ctmString'])   
            print("Candela 1 grandezza:", self.distanzaTraAperturaEChiusura(candle1))   
            print("Candela 2 orario:", candle2['ctmString'])   
            print("Candela 2 grandezza:", self.distanzaTraAperturaEChiusura(candle2))   

            if(self.lowPrice(candle1) < self.lowPrice(candle2)):
                self.stopLoss = self.lowPrice(candle1)
            else:
                self.stopLoss = self.lowPrice(candle2)

        return self.isGreen(candle1) and self.isRed(candle2) and  self.chiusura(candle1) > self.chiusura(candle2) and self.candela1InghiotteCandela2(candle1, candle2)

    def isBearishEngulfingFigure(self, candle1, candle2):
        if(self.isRed(candle1) and self.isGreen(candle2) and self.chiusura(candle1) < self.chiusura(candle2) and self.candela1InghiotteCandela2(candle1, candle2)):
            print("PATTERN isBearishEngulfingFigure")
            print("Candela 1 orario:", candle1['ctmString'])   
            print("Candela 1 grandezza:", self.distanzaTraAperturaEChiusura(candle1))   
            print("Candela 2 orario:", candle2['ctmString'])   
            print("Candela 2 grandezza:", self.distanzaTraAperturaEChiusura(candle2))   

            if(self.lowPrice(candle1) < self.lowPrice(candle2)):
                self.stopLoss = self.lowPrice(candle1)
            else:
                self.stopLoss = self.lowPrice(candle2)        
        
        return self.isRed(candle1) and self.isGreen(candle2) and self.chiusura(candle1) < self.chiusura(candle2) and self.candela1InghiotteCandela2(candle1, candle2)

    def vengoDaRialzo(self, candlesToCheck):
        # return self.chiusura(ultimaDelTrend) >  self.chiusura(penultimaDelTrend) > self.chiusura(terzultimaDelTrend) #TODO: vedere quante candle confrontare
        # return self.chiusura(ultimaDelTrend) >  self.chiusura(penultimaDelTrend)
        rialzo = False
        for i in range(len(candlesToCheck)-1):
            # print(f"questa: { self.chiusura(candlesToCheck[i])} maggiore di questa meno1: { self.chiusura(candlesToCheck[i+1])}")
            if( self.chiusura(candlesToCheck[i])> self.chiusura(candlesToCheck[i+1])):
                rialzo = True
            else:
                rialzo = False
                return rialzo

        return rialzo



    def vengoDaRibasso(self, candlesToCheck):
        # return self.chiusura(ultimaDelTrend) <  self.chiusura(penultimaDelTrend) < self.chiusura(terzultimaDelTrend) #TODO: vedere quante candle confrontare
        # return self.chiusura(ultimaDelTrend) <  self.chiusura(penultimaDelTrend)
        ribasso = False
        for i in range(len(candlesToCheck)-1):
            # print(f"questa: { self.chiusura(candlesToCheck[i])} minore di questa meno1: { self.chiusura(candlesToCheck[i+1])}")
            if( self.chiusura(candlesToCheck[i])< self.chiusura(candlesToCheck[i+1])):
                ribasso = True
            else:
                ribasso = False
                return ribasso
                
        return ribasso


    def trasformaPips(self, pips):
        return round(pips * (pow(10, self.pipsPrecision)),2)

    def isGreen(self, candle):
        return candle['close'] >= 0

    def isRed(self, candle):
        return candle['close'] < 0

    def isStarSignal(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):
        return self.isRed(currentMeno1) and self.chiusura(current) < self.chiusura(currentMeno1) and self.isStar(lastIsHammerOrStar) and self.vengoDaRialzo(candlesToCheck) and self.haveLittleBodyRib(lastIsHammerOrStar)
   
    def isHammerSignal(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):
        return self.isGreen(currentMeno1) and self.chiusura(current) > self.chiusura(currentMeno1) and self.isHammer(lastIsHammerOrStar) and self.vengoDaRibasso(candlesToCheck) and self.haveLittleBodyRialz(lastIsHammerOrStar)

    def isBullishEngulfingSignal(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):
        return self.isGreen(currentMeno1) and self.chiusura(current) > self.chiusura(currentMeno1) and self.isBullishEngulfingFigure(lastIsHammerOrStar, candlesToCheck[0]) and self.vengoDaRibasso(candlesToCheck)
    
    def isBearishEngulfingSignal(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):
        return self.isRed(currentMeno1) and self.chiusura(current) < self.chiusura(currentMeno1) and self.isBearishEngulfingFigure(lastIsHammerOrStar, candlesToCheck[0]) and self.vengoDaRialzo(candlesToCheck)
    
    def checkRibassistaInversion(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):

        if(self.isStarSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck) or self.isBearishEngulfingSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)):
        # if(self.isStarSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)):
            print("INVERSIONE RIBASSISTA")
            print(f"CHIUSURA CORRENTE: {self.chiusura(current)}")
            print(f"CANDELA PRECEDENTE ROSSA: {self.isRed(currentMeno1)}")
            print(f"CHIUSURA PRECEDENTE: {self.chiusura(currentMeno1)}")
            print(f"CHIUSURA CORRENTE MINORE DELLA PRECEDENTE: {self.chiusura(current) < self.chiusura(currentMeno1)}")
            print(f"HO UNA SHOOTING STAR: {self.isStar(lastIsHammerOrStar)}")
            # print(f"HO UN BEARUSH ENGULFING PATTERN: {self.isBearishEngulfingSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)}")
            print(f"STO VENENDO DA UN RIALZO: {self.vengoDaRialzo(candlesToCheck)}")
            print(f"ORARIO SEGNALE INVERSIONE: {lastIsHammerOrStar['ctmString']}")
            print("\n")


            return True
        else:
            return False

        


    def checkRialzistaInversion(self, current, currentMeno1, lastIsHammerOrStar, candlesToCheck):

        if(self.isHammerSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck) or self.isBullishEngulfingSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)):
        # if(self.isHammerSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)):

            print("INVERSIONE RIALZISTA")
            print(f"CHIUSURA CORRENTE: {self.chiusura(current)}")
            print(f"CANDELA PRECEDENTE VERDE: {self.isGreen(currentMeno1)}")
            print(f"CHIUSURA PRECEDENTE: {self.chiusura(currentMeno1)}")
            print(f"CHIUSURA CORRENTE MAGGIORE DELLA PRECEDENTE: {self.chiusura(current) > self.chiusura(currentMeno1)}")
            print(f"HO UNA HAMMER: {self.isHammer(lastIsHammerOrStar)}")
            # print(f"HO UN BULLISH ENGULFING PATTERN: {self.isBullishEngulfingSignal(current, currentMeno1, lastIsHammerOrStar, candlesToCheck)}")
            print(f"STO VENENDO DA UN RIBASSO: {self.vengoDaRibasso(candlesToCheck)}")
            print(f"ORARIO SEGNALE INVERSIONE: {lastIsHammerOrStar['ctmString']}")
            print("\n")

            return True
        else:
            return False


    def haveLittleBodyRib(self, candle):

        if(candle['close'] >= 0 ):

            if(abs(self.chiusura(candle) - self.exactPrice(candle['open'])) <= abs((self.highPrice(candle) - self.chiusura(candle))) / DIVISORE_GRANDEZZA_CANDELA):

                # print(f"RiBASSO candela verde: \nDifferenza tra chiusura e apertura(corpo): {abs(self.chiusura(candle) - self.exactPrice(candle['open']))}\n1/3 di ombra sup: {abs((self.highPrice(candle) - self.chiusura(candle))) / DIVISORE_GRANDEZZA_CANDELA} +")
                # print(f"abs((self.highPrice(candle) _> {abs(self.highPrice(candle))}")
                # print("LITTE BODY RIBASSO TRUE")

                # plotta(self.exactPrice(candle['open']) , self.chiusura(candle) , self.highPrice(candle), self.lowPrice(candle), candle['close'] )

                return True
        else:

            if(abs(self.chiusura(candle) - self.exactPrice(candle['open'])) <= abs((self.highPrice(candle) - self.exactPrice(candle['open']))) / DIVISORE_GRANDEZZA_CANDELA):
                # print(f"RiBASSO candela ROSSA: \nDifferenza tra chiusura e apertura(corpo): {abs(self.chiusura(candle) - self.exactPrice(candle['open']))}\n1/3 di ombra sup: {abs((self.highPrice(candle) - self.exactPrice(candle['open']))) / DIVISORE_GRANDEZZA_CANDELA} +")
                # print(f"abs((self.highPrice(candle) _> {abs(self.highPrice(candle))}")
                # print("LITTE BODY RIBASSO TRUE")
                # plotta(self.exactPrice(candle['open']) , self.chiusura(candle) , self.highPrice(candle), self.lowPrice(candle), candle['close'] )

                return True
        return False


    def haveLittleBodyRialz(self, candle):

        if(candle['close'] >= 0 ):

            if(abs(self.chiusura(candle) - self.exactPrice(candle['open'])) <= abs((self.lowPrice(candle) - self.exactPrice(candle['open']))) / DIVISORE_GRANDEZZA_CANDELA):
                # print(f"Rialzo candela verde: \nDifferenza tra chiusura e apertura(corpo): {abs(self.chiusura(candle) - self.exactPrice(candle['open']))}\n1/3 di ombra sup: {abs((self.lowPrice(candle) - self.exactPrice(candle['open']))) / DIVISORE_GRANDEZZA_CANDELA}")
                # print(f"abs((self.lowPrice(candle) _> {abs(self.lowPrice(candle))}")
                # print("LITTE BODY RIALZO TRUE")
                # plotta(self.exactPrice(candle['open']) , self.chiusura(candle) , self.highPrice(candle), self.lowPrice(candle), candle['close'] )

                return True
        else:

            if(abs(self.chiusura(candle) - self.exactPrice(candle['open'])) <= abs((self.lowPrice(candle) - self.chiusura(candle))) / DIVISORE_GRANDEZZA_CANDELA):
                # print(f"Rialzo candela rossa: \nDifferenza tra chiusura e apertura(corpo): {abs(self.chiusura(candle) - self.exactPrice(candle['open']))}\n1/3 di ombra sup: {abs((self.lowPrice(candle) - self.chiusura(candle))) / DIVISORE_GRANDEZZA_CANDELA}")
                # print(f"abs((self.lowPrice(candle) _> {abs(self.lowPrice(candle))}")
                # print("LITTE BODY RIALZO TRUE")
                # plotta(self.exactPrice(candle['open']) , self.chiusura(candle) , self.highPrice(candle), self.lowPrice(candle), candle['close'] )


                return True

        return False



    def getLastCharInfoForPeriod(self, period):

        if(period==1):
            self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART_1_MIN
        elif(period==5):
            self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART_5_MIN

        minutesAgo = datetime.datetime.now() - datetime.timedelta(minutes=self.minuti_timestamp_get_charts)

        minutesAgo = "{:10.3f}".format(minutesAgo.timestamp()).replace('.', '')

        lastChartsGeneralInfo = self.getSymbolChartInfo(int(minutesAgo), period)

        lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']


        while len(lastChartsInfo) < (PERIODO_RSI+1):
            self.minuti_timestamp_get_charts = self.minuti_timestamp_get_charts * 2
            minutesAgo = datetime.datetime.now() - datetime.timedelta(minutes=self.minuti_timestamp_get_charts)
            minutesAgo = "{:10.3f}".format(minutesAgo.timestamp()).replace('.', '')
            lastChartsGeneralInfo = self.getSymbolChartInfo(int(minutesAgo), period)
            lastChartsInfo = lastChartsGeneralInfo['returnData']['rateInfos']

            sleep(.3)

        return lastChartsInfo



    def calcolaRsi(self):

        lastChartsInfo = self.getLastCharInfoForPeriod(PERIODO_CHARTS)

        logger.debug(f'LAST CHARTS LENGTH: {len(lastChartsInfo)}')

        prezziChiusura = []

        for i in range(PERIODO_RSI):
                current = lastChartsInfo[i]
                prezziChiusura.append(current['open'] + current['close'])


        lastSymbolVal = self.getSymbol()
        bid = lastSymbolVal['returnData']['bid']
        ask = lastSymbolVal['returnData']['ask']
        prec = lastSymbolVal['returnData']['precision']

        # pr = round((bid + ask) / 2, prec) * (pow(10, prec))
        # print("BID", bid)
        # print("ASK", ask)

        prezziChiusura.append(bid * (pow(10, prec)))

        gains = []
        losses = []

        logger.debug(f"{prezziChiusura}")

        for i in range(PERIODO_RSI):
            difference = prezziChiusura[i+1] - prezziChiusura[i]
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

        # logger.info(f'RSI {round(rsi, 2)} - PERIODI:  {PERIODO_RSI}')
        # print(ff'RSI {round(rsi, 2)} - PERIODI:  {PERIODO_RSI}', end='\r')
        self.rsi = rsi
        return rsi

    def makeSomeMoney(self):
        while True:

            rsi = self.calcolaRsi()

            openedTrades = self.getOpenedTrades()['returnData']

            openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None) if len(openedTrades) > 0 else None

            if(len(openedTrades) <= 0 or openedTrade == None):


                lastChartsInfo = self.getLastCharInfoForPeriod(PERIODO_CHARTS)
                # lastChartsInfo = getCharts()

                lastChartsInfoReverted = lastChartsInfo


                current = lastChartsInfoReverted[len(lastChartsInfoReverted)-1]
                currentMeno1 = lastChartsInfoReverted[len(lastChartsInfoReverted)-2]
                lastIsHammerOrStar = lastChartsInfoReverted[len(lastChartsInfoReverted)-3]
                ultimaDelTrend = lastChartsInfoReverted[len(lastChartsInfoReverted)-4]
                penultimaDelTrend = lastChartsInfoReverted[len(lastChartsInfoReverted)-5]
                terzultimaDelTrend = lastChartsInfoReverted[len(lastChartsInfoReverted)-6]

                # self.checkRialzistaInversion(current, currentMeno1, lastIsHammerOrStar, [ultimaDelTrend, penultimaDelTrend])
                # self.checkRibassistaInversion(current, currentMeno1, lastIsHammerOrStar, [ultimaDelTrend, penultimaDelTrend])

                print(f'RSI: {round(rsi,2)}                                                              ',end="\r")

                # plotta(current['open'] / pow(10, self.precision), self.chiusura(current), self.highPrice(current), self.lowPrice(current), current['close'] )
                # plotta(currentMeno1['open'] / pow(10, self.precision), self.chiusura(currentMeno1), self.highPrice(currentMeno1), self.lowPrice(currentMeno1), currentMeno1['close'] )
                # plotta(lastIsHammerOrStar['open'] / pow(10, self.precision), self.chiusura(lastIsHammerOrStar), self.highPrice(lastIsHammerOrStar), self.lowPrice(lastIsHammerOrStar), lastIsHammerOrStar['close'] )
                # plotta(ultimaDelTrend['open'] / pow(10, self.precision), self.chiusura(ultimaDelTrend), self.highPrice(ultimaDelTrend), self.lowPrice(ultimaDelTrend), ultimaDelTrend['close'] )
                # plotta(penultimaDelTrend['open'] / pow(10, self.precision), self.chiusura(penultimaDelTrend), self.highPrice(penultimaDelTrend), self.lowPrice(penultimaDelTrend), penultimaDelTrend['close'] )
                # plotta(terzultimaDelTrend['open'] / pow(10, self.precision), self.chiusura(terzultimaDelTrend), self.highPrice(terzultimaDelTrend), self.lowPrice(terzultimaDelTrend), terzultimaDelTrend['close'] )

                if(self.checkRSIIfInBuyRange(rsi) and self.checkRialzistaInversion(current, currentMeno1, lastIsHammerOrStar, [ultimaDelTrend, penultimaDelTrend, terzultimaDelTrend])):

                        print("Compro analizzando da candela corrende delle:",current['ctmString'] )

                        self.openBuyTradeInversion(self.stopLoss)


                if(self.checkRSIIfInSellRange(rsi) and self.checkRibassistaInversion(current,currentMeno1, lastIsHammerOrStar, [ultimaDelTrend, penultimaDelTrend, terzultimaDelTrend])):
                        print("Vendo analizzando da candela corrende delle:",current['ctmString'] )

                        self.openSellTradeInversion(self.stopLoss)


            else:

                if(openedTrade != None):
                    profittoInPips = self.trasformaPips(openedTrade['close_price'] - openedTrade['open_price'])

                    # profitto = openedTrade['profit']
                    # profittoInPips = self.trasformaPips(openedTrade['close_price'] - openedTrade['open_price'])

                    # if(profitto == None):
                    #     symbolInfo = self.getSymbol()
                    #     prezzoAcquisto = symbolInfo['returnData']['bid']
                    #     prezzoVendita = symbolInfo['returnData']['ask']

                    #     profitto = self.calcolaProfitto(openedTrade['cmd'], openedTrade['open_price'], prezzoAcquisto if openedTrade['cmd'] == TransactionSide.BUY else prezzoVendita)
                    #     logger.info(f"\n#########\nError retrieving profit. Calculated profit: {profitto}\n#########")


                    print(f'RSI: {round(rsi,2)} - Profit: {GREEN} {profittoInPips} {RESET}      ',end="\r") if profittoInPips >= 0 else print(f'RSI: {round(rsi,2)} - Profit: {RED} {profittoInPips} {RESET}      ',end="\r")
                    # print(f'Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'Profit: {RED} {profitto} {RESET}      ',end="\r")



                    cmdd = openedTrade['cmd']

                    if((cmdd == TransactionSide.BUY and rsi > VALORE_ALTO_RSI and  openedTrade['offset'] <= 0 and profittoInPips>self.minimum_tp_value )):

                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_ALTO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_ALTO)['status']

                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")

                    elif((cmdd == TransactionSide.SELL and rsi < VALORE_BASSO_RSI and  openedTrade['offset'] <= 0 and profittoInPips>self.minimum_tp_value)):

                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_ALTO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_ALTO)['status']

                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")
                    elif((openedTrade['offset'] <= 0 and  profittoInPips>(self.minimum_tp_value*2))):
                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_BASSO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_BASSO)['status']

                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")


            sleep(1)


try:
    xtbot = XTBot(SYMBOL)
except Exception as e:
    logger.info(f"{e}")
    waitForClose()
