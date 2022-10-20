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
    def __init__(self, symbol, autostart=True):
        self.symbol = symbol
        self.checkSymbolConfig()
        self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART
        self.minimum_tp_value = MINIMUM_TP_VALUE * MULTYPLIER
        self.client = APIClient()
        self.login()
        self.symbolInfo = self.getSymbol()
        self.lotMin = self.symbolInfo['returnData']['lotMin'] * MULTYPLIER
        self.precision = self.symbolInfo['returnData']['precision']
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

    def openBuyTrade(self):

        symbolInfo = self.getSymbol()
        prezzoVendita = symbolInfo['returnData']['ask']
        precision = symbolInfo['returnData']['precision']
        pips = self.getCorrectStopLoss(TransactionSide.BUY, prezzoVendita, precision)
        sl = round(prezzoVendita - pips, precision)
        
        logger.info(f"\n#########\nOpen position: BUY\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.BUY, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']
        else:
            print("ERROR: ",order)

    def openSellTrade(self):

        symbolInfo = self.getSymbol()
        prezzoAcquisto = symbolInfo['returnData']['bid']
        precision = symbolInfo['returnData']['precision']
        pips = self.getCorrectStopLoss(TransactionSide.SELL, prezzoAcquisto, precision)
        sl = round(prezzoAcquisto + pips, precision)
       
        logger.info(f"\n#########\nOpen position: SELL\nFor: {SYMBOL}\nSL: {sl}\nLot:{self.lotMin}\nRSI:{self.rsi}\n#########")

        order = self.client.commandExecute('tradeTransaction', dict(tradeTransInfo=dict(cmd=TransactionSide.SELL, symbol=SYMBOL, price=TRADE_PRICE, sl=sl, tp=0, type=TransactionType.ORDER_OPEN, volume=self.lotMin)))
        if(order['status']):
            self.order = order['returnData']['order']
        else:
            print("ERROR: ",order)

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
        return(int(rsi) < (int(VALORE_BASSO_RSI)))
        # TODO: niente range co controllo operazione precedente
        # return(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)))
                    

    def checkRSIIfInSellRange(self, rsi):
        return(int(rsi) > (int(VALORE_ALTO_RSI)))
        # TODO: niente range co controllo operazione precedente
        # return(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)))
    
    # def checkIfLastTradeIsOk(self, cmd):
    #     yesterady = datetime.datetime.now() - datetime.timedelta(days=1)
    #     yesterady = "{:10.3f}".format(yesterady.timestamp()).replace('.', '')
    #     print(yesterady)
    #     trades = self.client.commandExecute('getTradesHistory', dict(end=0, start=int(yesterady)))['returnData']
    #     # trades = trades[::-1]
    #     trade = next((x for x in trades if x['symbol'] == SYMBOL and x['cmd'] == cmd), None) if len(trades) > 0 else None

    #     if(trade != None):
    #         if(trade['profit'] > 0):
    #             return True
    #         else:
    #             return False
    #     else:
    #         return True


    def chiusura(self, candle):
        return candle['open'] + candle['close']
    
    def highPrice(self, candle):
        return (candle['open'] + candle['high']) / pow(10, self.precision)

    def lowPrice(self, candle):
        return (candle['open'] + candle['low']) / pow(10, self.precision)

    def inversioneRibassista(self, candle):
        return abs(candle['high']) > abs(candle['low']*2)

    def inversioneRialzista(self, candle):
        return abs(candle['low']) > abs(candle['high']*2)

    def vengoDaRialzo(self, terzultima, quartultima, quintultima):
        return self.chiusura(terzultima) >  self.chiusura(quartultima) > self.chiusura(quintultima)


    def vengoDaRibasso(self, terzultima, quartultima, quintultima):
        return self.chiusura(terzultima) <  self.chiusura(quartultima) < self.chiusura(quintultima)

    def checkRibassistaInversion(self, current, last, terzultima, quartultima, quintultima):

        if(self.chiusura(current) < self.chiusura(last) and self.inversioneRibassista(last) and self.vengoDaRialzo(terzultima, quartultima, quintultima)):
            print("INVERSIONE RIBASSISTA")
            print(f"CHIUSURA CORRENTE: {self.chiusura(current)}")
            print(f"CHIUSURA PRECEDENTE: {self.chiusura(last)}")
            print(f"self.chiusura(current) < self.chiusura(last): {self.chiusura(current) < self.chiusura(last)}")
            print(f"self.inversioneRibassista(last): {self.inversioneRibassista(last)}")
            print(f"self.vengoDaRialzo(terzultima, quartultima, quintultima): {self.vengoDaRialzo(terzultima, quartultima, quintultima)}")
            print(f"MASSIMO PRECEDENTE: {last['high']}")
            print(f"MINIMO PRECEDENTE: {last['low']}")
            print(f"ORARIO: {last['ctmString']}")
            return True
        else:
            return False

    def checkRialzistaInversion(self, current, last, terzultima, quartultima, quintultima):

        if(self.chiusura(current) > self.chiusura(last) and self.inversioneRialzista(last) and self.vengoDaRibasso(terzultima, quartultima, quintultima)):
            print("INVERSIONE RIBASSISTA")
            print(f"CHIUSURA CORRENTE: {self.chiusura(current)}")
            print(f"CHIUSURA PRECEDENTE: {self.chiusura(last)}")
            print(f"self.chiusura(current) > self.chiusura(last): {self.chiusura(current) > self.chiusura(last)}")
            print(f"self.inversioneRialzista(last): {self.inversioneRialzista(last)}")
            print(f"self.vengoDaRialzo(terzultima, quartultima, quintultima): {self.vengoDaRibasso(terzultima, quartultima, quintultima)}")
            print(f"MASSIMO PRECEDENTE: {last['low']}")
            print(f"MINIMO PRECEDENTE: {last['high']}")
            print(f"ORARIO: {last['ctmString']}")
            print("\n\n")

            return True
        else:
            return False


    def getLastCharInfoForPeriod(self, period):

        if(period==1):
            self.minuti_timestamp_get_charts = MINUTI_TIMESTAMP_GET_CHART
        elif(period==5):
            self.minuti_timestamp_get_charts = 80
 
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

        # lastChartsInfoReverted = sorted(lastChartsInfo, key=lambda x: x['ctm'], reverse=True)

        logger.debug(f'LAST CHARTS LENGTH: {len(lastChartsInfo)}')

        prezziChiusura = []

        for i in range(PERIODO_RSI):
                current = lastChartsInfo[i]
                prezziChiusura.append(current['open'] + current['close'])

        # prezziChiusuraReverted = prezziChiusura[::-1]
        # prezziChiusura = prezziChiusura[::-1]

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
        # print(f'RSI 14 : {round(rsi, 2)}', end='\r')

        self.rsi = rsi

        return rsi
    
    def makeSomeMoney(self):
        while True:

            rsi = self.calcolaRsi()

            openedTrades = self.getOpenedTrades()['returnData']

            openedTrade = next((x for x in openedTrades if x['symbol'] == SYMBOL), None) if len(openedTrades) > 0 else None

            if(len(openedTrades) <= 0 or openedTrade == None):

                # logger.debug("Non ho trade aperti oppure non trovo un trade con qursto symbol")
                # logger.debug("RSI:", round(rsi,2))
                # logger.debug(f"RSI:{int(rsi)} BASSO: {int(VALORE_BASSO_RSI)} SCARTO: {int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)}")
                # logger.debug(f"RSI:{int(rsi)} ALTO: {int(VALORE_ALTO_RSI)} SCARTO: {int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)}")



                # logger.debug("previuoso rsi", self.previousRsi)
                # logger.debug("Currrenti rsi", rsi)
                # logger.debug("\n\n")
                
                # if(int(rsi) in range(int(VALORE_BASSO_RSI), int(VALORE_BASSO_RSI - VALORE_SCARTO_RSI)) and self.rialzo == True):
                # if((self.checkRSIIfInBuyRange(rsi) and self.rialzo == True) or (self.previousRsi != 0 and rsi > self.previousRsi and self.rialzo == True)):

                lastChartsInfo = self.getLastCharInfoForPeriod(PERIODO_CHARTS)

                lastChartsInfoReverted = lastChartsInfo

                current = lastChartsInfoReverted[len(lastChartsInfoReverted)-1]
                last = lastChartsInfoReverted[len(lastChartsInfoReverted)-2]
                terzultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-3]
                quartultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-4]
                quintultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-5]

                # print("CURRENT:", current['ctmString'])
                # print("last:", last['ctmString'])
                # print("terzultima:", terzultima['ctmString'])
                print(f'RSI: {round(rsi,2)}                                                              ',end="\r")

                if(self.checkRSIIfInBuyRange(rsi) and self.checkRialzistaInversion(current, last, terzultima, quartultima, quintultima)):

                        self.openBuyTradeInversion(self.lowPrice(last))
               
                # if(int(rsi) in range(int(VALORE_ALTO_RSI), int(VALORE_ALTO_RSI + VALORE_SCARTO_RSI)) and self.rialzo == False):
                # if((self.checkRSIIfInSellRange(rsi)and self.rialzo == False) or (self.previousRsi != 0 and rsi < self.previousRsi and self.rialzo == False)):
                if(self.checkRSIIfInSellRange(rsi) and self.checkRibassistaInversion(current, last, terzultima, quartultima, quintultima)):

                        self.openSellTradeInversion(self.highPrice(last))

                    
                # self.previousRsi = rsi

            else:
                
                if(openedTrade != None):

                    profitto = openedTrade['profit']
                    
                    if(profitto == None):
                        symbolInfo = self.getSymbol()
                        prezzoAcquisto = symbolInfo['returnData']['bid']
                        prezzoVendita = symbolInfo['returnData']['ask']
                        
                        profitto = self.calcolaProfitto(openedTrade['cmd'], openedTrade['open_price'], prezzoAcquisto if openedTrade['cmd'] == TransactionSide.BUY else prezzoVendita)
                        logger.info(f"\n#########\nError retrieving profit. Calculated profit: {profitto}\n#########")


                    print(f'RSI: {round(rsi,2)} - Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'RSI: {round(rsi,2)} - Profit: {RED} {profitto} {RESET}      ',end="\r")
                    # print(f'Profit: {GREEN} {profitto} {RESET}      ',end="\r") if profitto >= 0 else print(f'Profit: {RED} {profitto} {RESET}      ',end="\r")
                    
                    
                    
                    cmdd = openedTrade['cmd']

                    if((cmdd == TransactionSide.BUY and rsi > VALORE_ALTO_RSI and profitto != None and  openedTrade['offset'] <= 0 and profitto>self.minimum_tp_value )):

                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_ALTO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_ALTO)['status']
                        
                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")
                    
                    elif((cmdd == TransactionSide.SELL and rsi < VALORE_BASSO_RSI and profitto != None and  openedTrade['offset'] <= 0 and profitto>self.minimum_tp_value)):
                        
                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_ALTO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_ALTO)['status']

                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")
                    elif((openedTrade['offset'] <= 0 and  profitto>(self.minimum_tp_value*5))):
                        logger.info(f"\n#########\nModify position for order {openedTrade['order']}\nTrailing SL: {VALORE_TRALING_STOP_LOSS_BASSO}\n#########")
                        modifyResult = self.modifyTrade(openedTrade['order'], openedTrade['cmd'] , openedTrade['sl'], 0, VALORE_TRALING_STOP_LOSS_BASSO)['status']

                        print(f"Modify trade result: {GREEN} {modifyResult} {RESET}") if modifyResult == True else print(f"Modify trade result: {RED} {modifyResult} {RESET}")

                  
            sleep(1)


try:
    xtbot = XTBot(SYMBOL)
except Exception as e:
    logger.info(f"{e}")
    waitForClose()
