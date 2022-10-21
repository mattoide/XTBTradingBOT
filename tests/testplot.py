import matplotlib.pyplot as plt

import json


def getCharts():
    
    f = open('./tests/test.json')
    data = json.load(f)
    f.close()
    return data['returnData']['rateInfos']

def plotta(prezzoApertura, prezzoChiusura, alto, basso, close):
    # print("prezzoApertura", prezzoApertura)
    # print("prezzoChiusura", prezzoChiusura)
    # print("alto", alto)
    # print("basso", basso)
    # print("close", close)

    #corpo
    x = [1,1]
    y = [prezzoApertura,prezzoChiusura]

    #ombra sup
    a = [0,0]
    if(close>0):
        b = [prezzoChiusura,alto]
    else:
        b = [prezzoApertura,alto]


    #ombra inf
    c = [2,2]
    if(close>0):
        d = [prezzoApertura,basso]
    else:
        d = [prezzoChiusura,basso]
    
    
    plt.plot(x, y,linewidth=10)
    plt.plot(a, b,linewidth=10)
    plt.plot(c, d,linewidth=10)
    plt.show()
