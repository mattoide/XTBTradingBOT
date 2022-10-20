import json
import datetime


  
# PERIODO_RSI = 14
#   // 9.22 = 49.1

# Opening JSON file
f = open('tst.json')
  
# returns JSON object as 
# a dictionary

lastChartsInfo = json.load(f)['returnData']['rateInfos']

lastChartsInfoReverted = sorted(lastChartsInfo, key=lambda x: x['ctm'], reverse=False)

# print(f'LAST CHARTS LENGTH: {len(lastChartsInfoReverted)}')
  
# # Iterating through the json
# # # list
# # for i in lastChartsInfoReverted:
# #     print(i)
  
# # Closing file


# prezziChiusura = []
# precision = 5
# for i in range(PERIODO_RSI +1):
#         current = lastChartsInfoReverted[i]
#         prezziChiusura.append(round((current['open'] / pow(10, precision)) + (current['close']  / pow(10, precision)), precision))
#         print(f"ORA: {current['ctmString']} --- {current['open']} + {current['close']} ---  {current['open'] + current['close']}")

# prezziChiusuraReverted = prezziChiusura[::-1]
# # prezziChiusuraReverted = prezziChiusura 

# print(prezziChiusuraReverted)


# gains = []
# losses = []


# for i in range(PERIODO_RSI):
#     difference = prezziChiusuraReverted[i+1] - prezziChiusuraReverted[i]
#     if(difference>0):
#         gain = difference
#         loss = 0
#     elif(difference <0):
#         gain = 0
#         loss = abs(difference)
#     else:
#         gain = 0
#         loss = 0

#     gains.append(gain)
#     losses.append(loss)


# avg_gain = sum(gains) / len(gains)
# avg_loss = sum(losses) / len(losses)

# rs = avg_loss and avg_gain / avg_loss
# print(rs)

# rsi = 100 - (100 / (1 + rs))
# rsi = rsi -5.55


# print(f'RSI {rsi} - PERIODI:  {PERIODO_RSI}')


# f.close()

# yesterady = datetime.datetime.now() - datetime.timedelta(minutes=80)
# yesterady = "{:10.3f}".format(yesterady.timestamp()).replace('.', '')
# print(yesterady)

# analizzare candela 11:10 del EURGBP


# print(lastChartsInfoReverted[len(lastChartsInfoReverted)-1])
# print(lastChartsInfoReverted)

current = lastChartsInfoReverted[len(lastChartsInfoReverted)-1]
last = lastChartsInfoReverted[len(lastChartsInfoReverted)-2]
terzultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-3]
quartultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-4]
quintultima = lastChartsInfoReverted[len(lastChartsInfoReverted)-5]


def chiusura(candle):
    return candle['open'] + candle['close']

def inversioneRibassista(candle):
    return candle['high'] > candle['low']*2

def inversioneRialzista(candle):
    return candle['low'] < -candle['high']*2

def vengoDaRialzo(terzultima, quartultima, quintultima):
    return chiusura(terzultima) >  chiusura(quartultima) > chiusura(quintultima)


def vengoDaRibasso(terzultima, quartultima, quintultima):
    return chiusura(terzultima) <  chiusura(quartultima) < chiusura(quintultima)

def checkRibassistaInversion(current, last, terzultima, quartultima, quintultima):
    if(chiusura(current) < chiusura(last) and inversioneRibassista(last) and vengoDaRialzo(terzultima, quartultima, quintultima)):
        return True
    else:
        return False

def checkRialzistaInversion(current, last, terzultima, quartultima, quintultima):
    if(chiusura(current) > chiusura(last) and inversioneRialzista(last) and vengoDaRibasso(terzultima, quartultima, quintultima)):
        return True
    else:
        return False



print(checkRibassistaInversion(current, last, terzultima, quartultima, quintultima))
print(checkRialzistaInversion(current, last, terzultima, quartultima, quintultima))


yesterady = datetime.datetime.now() - datetime.timedelta(minutes=80)
yesterady = "{:10.3f}".format(yesterady.timestamp()).replace('.', '')
print(yesterady)

f.close()